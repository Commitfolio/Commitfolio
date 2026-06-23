export type {
  AnalysisJob,
  AnalysisJobEvent,
  EvidenceSummary,
} from "../../shared/api/commitfolio-api";

export type AnalysisJobState = "idle" | "creating" | "created" | "refreshing" | "error";
export type EvidenceState = "idle" | "running" | "loaded" | "error";
export type ProgressStreamState = "idle" | "connecting" | "streaming" | "closed" | "error" | "unsupported";
