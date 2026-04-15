import { useEffect, useMemo, useState } from "react";
import { fetchCurrentUser, getAuthStartUrl, logout, type AuthenticatedUser } from "./lib/api";

type SessionState = "loading" | "signed-out" | "signed-in";

function getStatusMessage(search: string): string | null {
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

export default function App() {
  const [sessionState, setSessionState] = useState<SessionState>("loading");
  const [user, setUser] = useState<AuthenticatedUser | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [logoutPending, setLogoutPending] = useState(false);

  const authStartUrl = useMemo(() => getAuthStartUrl(), []);
  const statusMessage = useMemo(() => getStatusMessage(window.location.search), []);

  useEffect(() => {
    async function loadSession() {
      try {
        const currentUser = await fetchCurrentUser();
        setUser(currentUser);
        setSessionState(currentUser ? "signed-in" : "signed-out");
      } catch (error) {
        setErrorMessage(
          error instanceof Error ? error.message : "Unknown error while loading session state.",
        );
        setSessionState("signed-out");
      }
    }

    void loadSession();
  }, []);

  async function handleLogout() {
    setLogoutPending(true);
    setErrorMessage(null);

    try {
      await logout();
      setUser(null);
      setSessionState("signed-out");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Logout failed.");
    } finally {
      setLogoutPending(false);
    }
  }

  return (
    <main className="shell">
      <section className="card">
        <span className="eyebrow">Commitfolio bootstrap</span>
        <h1>GitHub OAuth vertical slice</h1>
        <p className="lede">
          This screen validates the first auth-first harness path for Commitfolio: signed-out CTA,
          GitHub redirect, callback completion, session check, and logout.
        </p>

        {statusMessage ? <p className="notice success">{statusMessage}</p> : null}
        {errorMessage ? <p className="notice error">{errorMessage}</p> : null}

        <div className="panel">
          <h2>Session status</h2>
          {sessionState === "loading" ? <p>Checking current session...</p> : null}

          {sessionState === "signed-out" ? (
            <>
              <p>You are signed out. Start GitHub OAuth to create the local bootstrap session.</p>
              <a className="button primary" href={authStartUrl}>
                Continue with GitHub
              </a>
            </>
          ) : null}

          {sessionState === "signed-in" && user ? (
            <>
              <dl className="user-grid">
                <div>
                  <dt>GitHub login</dt>
                  <dd>@{user.github_login}</dd>
                </div>
                <div>
                  <dt>User id</dt>
                  <dd>{user.id}</dd>
                </div>
                <div>
                  <dt>Name</dt>
                  <dd>{user.name ?? "Not provided"}</dd>
                </div>
                <div>
                  <dt>Connected</dt>
                  <dd>{String(user.connected)}</dd>
                </div>
              </dl>
              <button className="button secondary" disabled={logoutPending} onClick={handleLogout}>
                {logoutPending ? "Signing out..." : "Log out"}
              </button>
            </>
          ) : null}
        </div>

        <div className="meta">
          <p>
            Frontend uses <code>{authStartUrl}</code> as the GitHub entry point.
          </p>
          <p>
            Configure <code>VITE_API_BASE_URL</code> when the backend is not running on{" "}
            <code>http://localhost:8000</code>.
          </p>
        </div>
      </section>
    </main>
  );
}
