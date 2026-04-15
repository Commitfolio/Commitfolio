export function getStatusMessage(search: string): string | null {
  const params = new URLSearchParams(search);

  if (params.get("auth") === "success") {
    return "GitHub authentication completed. Your session is now active.";
  }

  const authError = params.get("auth_error");

  if (!authError) {
    return null;
  }

  const messages: Record<string, string> = {
    invalid_state: "The GitHub callback state was invalid. Please try again.",
    missing_code: "GitHub did not provide an authorization code.",
    access_denied: "GitHub authorization was cancelled or denied.",
    backend_not_configured:
      "Backend GitHub OAuth credentials are missing. Add the backend env vars and try again.",
    oauth_exchange_failed: "GitHub token exchange failed. Check backend credentials and try again.",
    oauth_profile_failed: "GitHub user lookup failed. Check backend credentials and try again.",
  };

  return messages[authError] ?? "Authentication failed. Check the backend logs and try again.";
}
