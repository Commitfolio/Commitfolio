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
    throw new Error("Failed to fetch session state.");
  }

  return (await response.json()) as AuthenticatedUser;
}

export async function fetchRepositories(
  visibility: RepositoryVisibility = "all",
): Promise<RepositoryListResponse> {
  const params = new URLSearchParams({ visibility });
  const response = await fetch(`${API_BASE_URL}/api/v1/repositories?${params.toString()}`, {
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error(await getErrorMessage(response, "Failed to fetch repositories."));
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
    throw new Error(await getErrorMessage(response, "Failed to create analysis job."));
  }

  return (await response.json()) as AnalysisJob;
}

export async function fetchAnalysisJob(jobId: string): Promise<AnalysisJob> {
  const response = await fetch(`${API_BASE_URL}/api/v1/analysis-jobs/${jobId}`, {
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error(await getErrorMessage(response, "Failed to fetch analysis job."));
  }

  return (await response.json()) as AnalysisJob;
}

export async function logout(): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/v1/auth/logout`, {
    method: "POST",
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error(await getErrorMessage(response, "Failed to log out."));
  }
}

async function getErrorMessage(response: Response, fallback: string): Promise<string> {
  try {
    const payload = (await response.json()) as { error?: { message?: string } };
    return payload.error?.message ?? fallback;
  } catch {
    return fallback;
  }
}
