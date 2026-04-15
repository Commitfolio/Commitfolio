export type AuthenticatedUser = {
  id: string;
  github_login: string;
  connected: true;
  name: string | null;
  avatar_url: string | null;
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

export async function logout(): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/v1/auth/logout`, {
    method: "POST",
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error("Failed to log out.");
  }
}
