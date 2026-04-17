import { getKoreanErrorMessage } from "./error-messages";

export type AuthenticatedUser = {
  id: string;
  github_login: string;
  connected: true;
  name: string | null;
  avatar_url: string | null;
};

export type RepositoryVisibility = "all" | "public" | "private";

export type RepositorySummary = {
  id: number;
  full_name: string;
  private: boolean;
  owner_type: string;
  default_branch: string;
  permissions: {
    admin: boolean;
    push: boolean;
    pull: boolean;
  };
  html_url: string;
  description: string | null;
  updated_at: string | null;
};

export type RepositoryListResponse = {
  items: RepositorySummary[];
  next_cursor: string | null;
};

export type AnalysisJob = {
  job_id: string;
  status: string;
  repository_full_name: string;
  branch: string;
  progress: {
    stage: string;
    percent: number;
  };
  result_id: string | null;
  failure_reason: string | null;
};

export type AnalysisJobEvent = {
  sequence: number;
  event_type: string;
  stage: string;
  percent: number;
  message: string;
  payload_json: Record<string, unknown>;
  created_at: string;
};

export type EvidenceSummary = {
  job_id: string;
  total_count: number;
  counts: Record<string, number>;
  latest_events: AnalysisJobEvent[];
};

export type AnalysisRunResponse = {
  job: AnalysisJob;
  evidence: EvidenceSummary;
};

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export function getAuthStartUrl(): string {
  return `${API_BASE_URL}/api/v1/auth/github/start`;
}

export async function fetchCurrentUser(): Promise<AuthenticatedUser | null> {
  const response = await fetch(`${API_BASE_URL}/api/v1/me`, {
    credentials: "include",
  });

  if (response.status === 401) {
    return null;
  }

  if (!response.ok) {
    throw new Error("세션 상태를 불러오지 못했습니다.");
  }

  return (await response.json()) as AuthenticatedUser;
}

export async function fetchRepositories(
  visibility: RepositoryVisibility = "all",
  cursor?: string | null,
): Promise<RepositoryListResponse> {
  const params = new URLSearchParams({ visibility });
  if (cursor) {
    params.set("cursor", cursor);
  }
  const response = await fetch(`${API_BASE_URL}/api/v1/repositories?${params.toString()}`, {
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error(await getErrorMessage(response, "저장소 목록을 불러오지 못했습니다."));
  }

  return (await response.json()) as RepositoryListResponse;
}

export async function createAnalysisJob(repository: RepositorySummary): Promise<AnalysisJob> {
  const response = await fetch(`${API_BASE_URL}/api/v1/analysis-jobs`, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      repository_full_name: repository.full_name,
      branch: repository.default_branch,
      github_repo_id: repository.id,
      private: repository.private,
      owner_type: repository.owner_type,
      default_branch: repository.default_branch,
      html_url: repository.html_url,
      description: repository.description,
    }),
  });

  if (!response.ok) {
    throw new Error(await getErrorMessage(response, "분석 작업을 만들지 못했습니다."));
  }

  return (await response.json()) as AnalysisJob;
}

export async function fetchAnalysisJob(jobId: string): Promise<AnalysisJob> {
  const response = await fetch(`${API_BASE_URL}/api/v1/analysis-jobs/${jobId}`, {
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error(await getErrorMessage(response, "분석 작업 상태를 불러오지 못했습니다."));
  }

  return (await response.json()) as AnalysisJob;
}

export async function runAnalysisJob(jobId: string): Promise<AnalysisRunResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/analysis-jobs/${jobId}/run`, {
    method: "POST",
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error(await getErrorMessage(response, "분석을 실행하지 못했습니다."));
  }

  return (await response.json()) as AnalysisRunResponse;
}

export async function fetchEvidenceSummary(jobId: string): Promise<EvidenceSummary> {
  const response = await fetch(`${API_BASE_URL}/api/v1/analysis-jobs/${jobId}/evidence`, {
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error(await getErrorMessage(response, "분석 근거 요약을 불러오지 못했습니다."));
  }

  return (await response.json()) as EvidenceSummary;
}

export function getAnalysisJobEventsUrl(jobId: string, after?: number): string {
  const params = new URLSearchParams();
  if (after !== undefined) {
    params.set("after", String(after));
  }

  const query = params.toString();
  return `${API_BASE_URL}/api/v1/analysis-jobs/${jobId}/events${query ? `?${query}` : ""}`;
}

export async function logout(): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/v1/auth/logout`, {
    method: "POST",
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error(await getErrorMessage(response, "로그아웃하지 못했습니다."));
  }
}

async function getErrorMessage(response: Response, fallback: string): Promise<string> {
  try {
    const payload = (await response.json()) as { error?: { code?: string; message?: string } };
    return getKoreanErrorMessage(payload.error?.code, payload.error?.message ?? fallback);
  } catch {
    return fallback;
  }
}

export type PortfolioEvidenceLink = {
  section_key: string;
  label: string;
  url: string;
  evidence_id: string;
};

export type PortfolioResult = {
  result_id: string;
  analysis_job_id: string;
  repository_full_name: string;
  version: number;
  headline: string;
  project_overview: string;
  role_summary: string;
  key_contributions: string[];
  tech_stack: string[];
  evidence_summary: string;
  interview_questions: string[];
  enhancement_status: string;
  enhancement_model: string | null;
  enhancement_message: string;
  evidence_links: PortfolioEvidenceLink[];
  created_at: string;
  updated_at: string;
};

export type PortfolioResultListItem = {
  result_id: string;
  analysis_job_id: string;
  repository_full_name: string;
  headline: string;
  version: number;
  created_at: string;
  updated_at: string;
};

export type PortfolioResultList = {
  items: PortfolioResultListItem[];
};

export async function generatePortfolioResult(jobId: string): Promise<PortfolioResult> {
  const response = await fetch(`${API_BASE_URL}/api/v1/analysis-jobs/${jobId}/result`, {
    method: "POST",
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error(await getErrorMessage(response, "포트폴리오 결과를 생성하지 못했습니다."));
  }

  return (await response.json()) as PortfolioResult;
}

export async function fetchPortfolioResult(resultId: string): Promise<PortfolioResult> {
  const response = await fetch(`${API_BASE_URL}/api/v1/results/${resultId}`, {
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error(await getErrorMessage(response, "포트폴리오 결과를 불러오지 못했습니다."));
  }

  return (await response.json()) as PortfolioResult;
}

export async function fetchPortfolioResults(): Promise<PortfolioResultList> {
  const response = await fetch(`${API_BASE_URL}/api/v1/results`, {
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error(await getErrorMessage(response, "최근 포트폴리오 결과를 불러오지 못했습니다."));
  }

  return (await response.json()) as PortfolioResultList;
}

export type PortfolioResultUpdateRequest = {
  headline?: string;
  project_overview?: string;
  role_summary?: string;
  key_contributions?: string[];
  tech_stack?: string[];
  evidence_summary?: string;
  interview_questions?: string[];
};

export async function updatePortfolioResult(
  resultId: string,
  payload: PortfolioResultUpdateRequest,
): Promise<PortfolioResult> {
  const response = await fetch(`${API_BASE_URL}/api/v1/results/${resultId}`, {
    method: "PATCH",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(await getErrorMessage(response, "포트폴리오 결과를 저장하지 못했습니다."));
  }

  return (await response.json()) as PortfolioResult;
}

export async function regeneratePortfolioResult(resultId: string): Promise<PortfolioResult> {
  const response = await fetch(`${API_BASE_URL}/api/v1/results/${resultId}/regenerate`, {
    method: "POST",
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error(await getErrorMessage(response, "포트폴리오 결과를 다시 생성하지 못했습니다."));
  }

  return (await response.json()) as PortfolioResult;
}
