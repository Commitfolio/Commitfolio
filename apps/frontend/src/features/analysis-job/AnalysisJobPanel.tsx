import type {
  AnalysisJob,
  AnalysisJobEvent,
  AnalysisJobState,
  EvidenceState,
  EvidenceSummary,
  ProgressStreamState,
} from "../../entities/analysis-job/analysis-job.types";
import type { RepositorySummary } from "../../entities/repository/repository.types";

type AnalysisJobPanelProps = {
  analysisJob: AnalysisJob | null;
  analysisJobError: string | null;
  analysisJobState: AnalysisJobState;
  evidenceError: string | null;
  evidenceState: EvidenceState;
  evidenceSummary: EvidenceSummary | null;
  progressEvents: AnalysisJobEvent[];
  progressStreamError: string | null;
  progressStreamState: ProgressStreamState;
  selectedRepository: RepositorySummary;
  onCreateAnalysisJob: () => void;
  onRefreshAnalysisJob: () => void;
  onGenerateResult: () => void;
  onRunAnalysisJob: () => void;
  resultGenerationDisabled: boolean;
  resultGenerationLabel: string;
};

export function AnalysisJobPanel({
  analysisJob,
  analysisJobError,
  analysisJobState,
  evidenceError,
  evidenceState,
  evidenceSummary,
  progressEvents,
  progressStreamError,
  progressStreamState,
  selectedRepository,
  onCreateAnalysisJob,
  onGenerateResult,
  onRefreshAnalysisJob,
  onRunAnalysisJob,
  resultGenerationDisabled,
  resultGenerationLabel,
}: AnalysisJobPanelProps) {
  const visibleEvents = progressEvents.length > 0 ? progressEvents : evidenceSummary?.latest_events ?? [];

  return (
    <div className="selected-repository">
      <span className="eyebrow subtle">Selected</span>
      <p>
        <strong>{selectedRepository.full_name}</strong> is ready for the next Stage 2 analysis job
        bootstrap.
      </p>
      <button
        className="button primary"
        disabled={analysisJobState === "creating"}
        onClick={onCreateAnalysisJob}
        type="button"
      >
        {analysisJobState === "creating" ? "Creating job..." : "Create analysis job"}
      </button>

      {analysisJobError ? <p className="notice error">{analysisJobError}</p> : null}

      {analysisJob ? (
        <div className="job-summary">
          <div>
            <span className="eyebrow subtle">Analysis job</span>
            <h3>{analysisJob.job_id}</h3>
          </div>
          <dl className="user-grid">
            <div>
              <dt>Status</dt>
              <dd>{analysisJob.status}</dd>
            </div>
            <div>
              <dt>Repository</dt>
              <dd>{analysisJob.repository_full_name}</dd>
            </div>
            <div>
              <dt>Branch</dt>
              <dd>{analysisJob.branch}</dd>
            </div>
            <div>
              <dt>Progress</dt>
              <dd>
                {analysisJob.progress.stage} · {analysisJob.progress.percent}%
              </dd>
            </div>
          </dl>
          {analysisJob.failure_reason ? <p className="notice error">{analysisJob.failure_reason}</p> : null}
          <button
            className="button secondary"
            disabled={analysisJobState === "refreshing"}
            onClick={onRefreshAnalysisJob}
            type="button"
          >
            {analysisJobState === "refreshing" ? "Refreshing..." : "Refresh status"}
          </button>
          <button
            className="button primary"
            disabled={evidenceState === "running"}
            onClick={onRunAnalysisJob}
            type="button"
          >
            {evidenceState === "running" ? "Running analysis..." : "Run analysis"}
          </button>
          <button
            className="button secondary"
            disabled={resultGenerationDisabled}
            onClick={onGenerateResult}
            type="button"
          >
            {resultGenerationLabel}
          </button>
          <div className="stream-status" aria-live="polite">
            Progress stream: {progressStreamState}
          </div>
          {progressStreamError ? <p className="notice error">{progressStreamError}</p> : null}
          {evidenceError ? <p className="notice error">{evidenceError}</p> : null}
          {evidenceSummary ? (
            <div className="evidence-summary">
              <div>
                <span className="eyebrow subtle">Evidence</span>
                <h3>{evidenceSummary.total_count} item(s) collected</h3>
              </div>
              <dl className="user-grid">
                {Object.entries(evidenceSummary.counts).map(([sourceType, count]) => (
                  <div key={sourceType}>
                    <dt>{sourceType}</dt>
                    <dd>{count}</dd>
                  </div>
                ))}
              </dl>
              {visibleEvents.length > 0 ? (
                <ul className="event-list" aria-label="Latest analysis events">
                  {visibleEvents.map((event) => (
                    <li key={event.sequence}>
                      <strong>#{event.sequence}</strong> {event.message}
                    </li>
                  ))}
                </ul>
              ) : null}
            </div>
          ) : null}
          <p className="privacy-note">
            Stage 4 streams replayable progress from the durable job event log. Refresh status remains
            available as the recovery source of truth.
          </p>
        </div>
      ) : null}
    </div>
  );
}
