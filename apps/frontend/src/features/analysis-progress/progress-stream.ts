import type { AnalysisJobEvent } from "../../entities/analysis-job/analysis-job.types";

export function getStoredLastSequence(jobId: string): number | undefined {
  const stored = sessionStorage.getItem(getLastSequenceStorageKey(jobId));
  if (!stored) {
    return undefined;
  }

  const parsed = Number.parseInt(stored, 10);
  return Number.isFinite(parsed) && parsed >= 0 ? parsed : undefined;
}

export function persistLastSequence(jobId: string, sequence: number) {
  sessionStorage.setItem(getLastSequenceStorageKey(jobId), String(sequence));
}

export function clearStoredLastSequence(jobId: string) {
  sessionStorage.removeItem(getLastSequenceStorageKey(jobId));
}

export function appendProgressEvent(events: AnalysisJobEvent[], nextEvent: AnalysisJobEvent) {
  return [...events.filter((event) => event.sequence !== nextEvent.sequence), nextEvent]
    .sort((left, right) => left.sequence - right.sequence)
    .slice(-8);
}

function getLastSequenceStorageKey(jobId: string) {
  return `analysis-job:${jobId}:last-sequence`;
}

export function parseSsePayload<T>(event: Event): T | null {
  const message = event as MessageEvent<string>;

  try {
    return JSON.parse(message.data) as T;
  } catch {
    return null;
  }
}
