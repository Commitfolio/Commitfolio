import { useCallback, useEffect, useRef, useState } from "react";
import type {
  AnalysisJob,
  AnalysisJobEvent,
  AnalysisJobState,
  EvidenceState,
  EvidenceSummary,
  ProgressStreamState,
} from "../../entities/analysis-job/analysis-job.types";
import type { RepositorySummary } from "../../entities/repository/repository.types";
import {
  appendProgressEvent,
  clearStoredLastSequence,
  getStoredLastSequence,
  parseSsePayload,
  persistLastSequence,
} from "../analysis-progress/progress-stream";
import {
  createAnalysisJob,
  fetchAnalysisJob,
  fetchEvidenceSummary,
  getAnalysisJobEventsUrl,
  runAnalysisJob,
} from "../../shared/api/commitfolio-api";

export function useAnalysisJobFlow() {
  const [analysisJobState, setAnalysisJobState] = useState<AnalysisJobState>("idle");
  const [analysisJob, setAnalysisJob] = useState<AnalysisJob | null>(null);
  const [analysisJobError, setAnalysisJobError] = useState<string | null>(null);
  const [evidenceState, setEvidenceState] = useState<EvidenceState>("idle");
  const [evidenceSummary, setEvidenceSummary] = useState<EvidenceSummary | null>(null);
  const [evidenceError, setEvidenceError] = useState<string | null>(null);
  const [progressStreamState, setProgressStreamState] = useState<ProgressStreamState>("idle");
  const [progressStreamError, setProgressStreamError] = useState<string | null>(null);
  const [progressEvents, setProgressEvents] = useState<AnalysisJobEvent[]>([]);
  const eventSourceRef = useRef<EventSource | null>(null);

  const closeProgressStream = useCallback(() => {
    eventSourceRef.current?.close();
    eventSourceRef.current = null;
  }, []);

  const resetAnalysisJob = useCallback(() => {
    closeProgressStream();
    setAnalysisJobState("idle");
    setAnalysisJob(null);
    setAnalysisJobError(null);
    setEvidenceState("idle");
    setEvidenceSummary(null);
    setEvidenceError(null);
    setProgressStreamState("idle");
    setProgressStreamError(null);
    setProgressEvents([]);
  }, [closeProgressStream]);

  useEffect(() => {
    return () => {
      closeProgressStream();
    };
  }, [closeProgressStream]);

  async function handleCreateAnalysisJob(repository: RepositorySummary) {
    setAnalysisJobState("creating");
    setAnalysisJobError(null);

    try {
      const createdJob = await createAnalysisJob(repository);
      setAnalysisJob(createdJob);
      setAnalysisJobState("created");
    } catch (error) {
      setAnalysisJobError(
        error instanceof Error ? error.message : "Unknown error while creating the analysis job.",
      );
      setAnalysisJobState("error");
    }
  }

  async function handleRefreshAnalysisJob() {
    if (!analysisJob) {
      return;
    }

    setAnalysisJobState("refreshing");
    setAnalysisJobError(null);

    try {
      const refreshedJob = await fetchAnalysisJob(analysisJob.job_id);
      setAnalysisJob(refreshedJob);
      setAnalysisJobState("created");

      if (refreshedJob.status === "completed" || evidenceSummary) {
        const summary = await fetchEvidenceSummary(refreshedJob.job_id);
        setEvidenceSummary(summary);
        setEvidenceState("loaded");
      }
    } catch (error) {
      setAnalysisJobError(
        error instanceof Error ? error.message : "Unknown error while refreshing the analysis job.",
      );
      setAnalysisJobState("error");
    }
  }

  async function handleRunAnalysisJob() {
    if (!analysisJob) {
      return;
    }

    clearStoredLastSequence(analysisJob.job_id);
    setProgressEvents([]);
    setEvidenceSummary(null);
    setEvidenceState("running");
    setEvidenceError(null);
    startProgressStream(analysisJob.job_id);

    try {
      const runResponse = await runAnalysisJob(analysisJob.job_id);
      setAnalysisJob(runResponse.job);
      setAnalysisJobState("created");
      setEvidenceSummary(runResponse.evidence);
      setProgressEvents(runResponse.evidence.latest_events);
      setEvidenceState("loaded");
    } catch (error) {
      setEvidenceError(error instanceof Error ? error.message : "Unknown error while running analysis.");
      setEvidenceState("error");

      try {
        const refreshedJob = await fetchAnalysisJob(analysisJob.job_id);
        setAnalysisJob(refreshedJob);
      } catch {
        // Keep the previous job snapshot if the failure status lookup also fails.
      }
    }
  }

  function startProgressStream(jobId: string) {
    closeProgressStream();
    setProgressStreamError(null);

    if (typeof EventSource === "undefined") {
      setProgressStreamState("unsupported");
      return;
    }

    const lastSequence = getStoredLastSequence(jobId);
    const source = new EventSource(getAnalysisJobEventsUrl(jobId, lastSequence), {
      withCredentials: true,
    });
    eventSourceRef.current = source;
    setProgressStreamState("connecting");

    source.onopen = () => {
      setProgressStreamState("streaming");
      setProgressStreamError(null);
    };
    source.onerror = () => {
      setProgressStreamState("error");
      setProgressStreamError("Progress stream disconnected. Reconnecting, or use Refresh status to recover.");
      void recoverAnalysisJobSnapshot(jobId);
    };

    source.addEventListener("snapshot", (event) => {
      const payload = parseSsePayload<{ job?: AnalysisJob }>(event);
      if (payload?.job) {
        setAnalysisJob(payload.job);
      }
    });

    for (const eventName of ["progress", "job_completed", "job_failed"] as const) {
      source.addEventListener(eventName, (event) => {
        const payload = parseSsePayload<AnalysisJobEvent & { job_id: string }>(event);
        if (!payload) {
          return;
        }

        persistLastSequence(jobId, payload.sequence);
        const progressEvent: AnalysisJobEvent = {
          sequence: payload.sequence,
          event_type: payload.event_type,
          stage: payload.stage,
          percent: payload.percent,
          message: payload.message,
          payload_json: payload.payload_json,
          created_at: payload.created_at,
        };
        setProgressEvents((events) => appendProgressEvent(events, progressEvent));
        setAnalysisJob((currentJob) =>
          currentJob
            ? {
                ...currentJob,
                status: eventName === "job_completed" ? "completed" : eventName === "job_failed" ? "failed" : "running",
                progress: {
                  stage: payload.stage,
                  percent: payload.percent,
                },
                failure_reason: eventName === "job_failed" ? payload.message : currentJob.failure_reason,
              }
            : currentJob,
        );

        if (eventName === "job_completed" || eventName === "job_failed") {
          setProgressStreamState("closed");
          closeProgressStream();
        }
      });
    }

    source.addEventListener("heartbeat", () => {
      setProgressStreamState("streaming");
      setProgressStreamError(null);
    });
  }

  async function recoverAnalysisJobSnapshot(jobId: string) {
    try {
      const refreshedJob = await fetchAnalysisJob(jobId);
      setAnalysisJob(refreshedJob);

      if (refreshedJob.status === "completed" || refreshedJob.status === "failed") {
        const summary = await fetchEvidenceSummary(jobId);
        setEvidenceSummary(summary);
        setProgressEvents(summary.latest_events);
        setEvidenceState("loaded");
      }
    } catch {
      // Keep the latest visible snapshot; the manual Refresh action remains the recovery fallback.
    }
  }

  return {
    analysisJob,
    analysisJobError,
    analysisJobState,
    evidenceError,
    evidenceState,
    evidenceSummary,
    handleCreateAnalysisJob,
    handleRefreshAnalysisJob,
    handleRunAnalysisJob,
    progressEvents,
    progressStreamError,
    progressStreamState,
    resetAnalysisJob,
  };
}
