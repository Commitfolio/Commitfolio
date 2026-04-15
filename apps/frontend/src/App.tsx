import { useEffect, useMemo, useState } from "react";
import {
  createAnalysisJob,
  fetchAnalysisJob,
  fetchCurrentUser,
  fetchRepositories,
  getAuthStartUrl,
  logout,
  type AnalysisJob,
  type AuthenticatedUser,
  type RepositorySummary,
  type RepositoryVisibility,
} from "./lib/api";

type SessionState = "loading" | "signed-out" | "signed-in";
type RepositoryState = "idle" | "loading" | "loaded" | "error";
type AnalysisJobState = "idle" | "creating" | "created" | "refreshing" | "error";

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
  const [repositoryState, setRepositoryState] = useState<RepositoryState>("idle");
  const [repositoryVisibility, setRepositoryVisibility] = useState<RepositoryVisibility>("all");
  const [repositories, setRepositories] = useState<RepositorySummary[]>([]);
  const [selectedRepository, setSelectedRepository] = useState<RepositorySummary | null>(null);
  const [repositoryError, setRepositoryError] = useState<string | null>(null);
  const [analysisJobState, setAnalysisJobState] = useState<AnalysisJobState>("idle");
  const [analysisJob, setAnalysisJob] = useState<AnalysisJob | null>(null);
  const [analysisJobError, setAnalysisJobError] = useState<string | null>(null);

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

  useEffect(() => {
    if (sessionState !== "signed-in") {
      setRepositoryState("idle");
      setRepositories([]);
      setSelectedRepository(null);
      setRepositoryError(null);
      resetAnalysisJob();
      return;
    }

    let cancelled = false;

    async function loadRepositories() {
      setRepositoryState("loading");
      setRepositoryError(null);
      setSelectedRepository(null);
      resetAnalysisJob();

      try {
        const response = await fetchRepositories(repositoryVisibility);

        if (cancelled) {
          return;
        }

        setRepositories(response.items);
        setRepositoryState("loaded");
      } catch (error) {
        if (cancelled) {
          return;
        }

        setRepositories([]);
        setRepositoryError(
          error instanceof Error ? error.message : "Unknown error while loading repositories.",
        );
        setRepositoryState("error");
      }
    }

    void loadRepositories();

    return () => {
      cancelled = true;
    };
  }, [repositoryVisibility, sessionState]);

  async function handleLogout() {
    setLogoutPending(true);
    setErrorMessage(null);

    try {
      await logout();
      setUser(null);
      setSessionState("signed-out");
      setRepositories([]);
      resetAnalysisJob();
      setSelectedRepository(null);
      setRepositoryState("idle");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Logout failed.");
    } finally {
      setLogoutPending(false);
    }
  }

  async function handleCreateAnalysisJob() {
    if (!selectedRepository) {
      return;
    }

    setAnalysisJobState("creating");
    setAnalysisJobError(null);

    try {
      const createdJob = await createAnalysisJob(selectedRepository);
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
    } catch (error) {
      setAnalysisJobError(
        error instanceof Error ? error.message : "Unknown error while refreshing the analysis job.",
      );
      setAnalysisJobState("error");
    }
  }

  function resetAnalysisJob() {
    setAnalysisJobState("idle");
    setAnalysisJob(null);
    setAnalysisJobError(null);
  }

  return (
    <main className="shell">
      <section className="card">
        <span className="eyebrow">Commitfolio bootstrap</span>
        <h1>Choose the repository to turn into a portfolio</h1>
        <p className="lede">
          Commitfolio starts with GitHub OAuth, then asks you to choose one repository. Stage 1 reads
          repository metadata only; commits, pull requests, issues, reviews, and changed files are
          collected in later analysis stages.
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

        {sessionState === "signed-in" ? (
          <section className="panel repository-panel" aria-labelledby="repository-selector-title">
            <div className="section-heading">
              <div>
                <span className="eyebrow subtle">Stage 1</span>
                <h2 id="repository-selector-title">Repository selector</h2>
              </div>
              <label className="filter-control">
                <span>Visibility</span>
                <select
                  aria-label="Repository visibility"
                  value={repositoryVisibility}
                  onChange={(event) =>
                    setRepositoryVisibility(event.target.value as RepositoryVisibility)
                  }
                >
                  <option value="all">All</option>
                  <option value="public">Public</option>
                  <option value="private">Private</option>
                </select>
              </label>
            </div>

            <p className="privacy-note">
              We list repositories available to your GitHub OAuth session so you can choose one
              project. This step shows metadata such as name, owner type, visibility, default branch,
              and basic permissions.
            </p>

            {repositoryState === "loading" ? <p>Loading accessible repositories...</p> : null}
            {repositoryState === "error" ? (
              <p className="notice error">{repositoryError ?? "Failed to load repositories."}</p>
            ) : null}
            {repositoryState === "loaded" && repositories.length === 0 ? (
              <p className="empty-state">
                No repositories were returned for this visibility filter. Try a different filter or
                confirm the OAuth app has the repository scopes you expect.
              </p>
            ) : null}

            {repositories.length > 0 ? (
              <ul className="repository-list" aria-label="Accessible repositories">
                {repositories.map((repository) => {
                  const isSelected = selectedRepository?.id === repository.id;

                  return (
                    <li key={repository.id} className={isSelected ? "repository selected" : "repository"}>
                      <button
                        type="button"
                        className="repository-button"
                        aria-pressed={isSelected}
                        aria-label={`Select ${repository.full_name}`}
                        onClick={() => {
                          setSelectedRepository(repository);
                          resetAnalysisJob();
                        }}
                      >
                        <span className="repository-main">
                          <span className="repository-name">{repository.full_name}</span>
                          <span className="repository-description">
                            {repository.description ?? "No description provided."}
                          </span>
                        </span>
                        <span className="repository-meta">
                          <span className={repository.private ? "badge private" : "badge public"}>
                            {repository.private ? "Private" : "Public"}
                          </span>
                          <span className="badge">{repository.owner_type}</span>
                          <span className="badge">Default: {repository.default_branch}</span>
                        </span>
                      </button>
                    </li>
                  );
                })}
              </ul>
            ) : null}

            {selectedRepository ? (
              <div className="selected-repository">
                <span className="eyebrow subtle">Selected</span>
                <p>
                  <strong>{selectedRepository.full_name}</strong> is ready for the next Stage 2
                  analysis job bootstrap.
                </p>
                <button
                  className="button primary"
                  disabled={analysisJobState === "creating"}
                  onClick={handleCreateAnalysisJob}
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
                    {analysisJob.failure_reason ? (
                      <p className="notice error">{analysisJob.failure_reason}</p>
                    ) : null}
                    <button
                      className="button secondary"
                      disabled={analysisJobState === "refreshing"}
                      onClick={handleRefreshAnalysisJob}
                      type="button"
                    >
                      {analysisJobState === "refreshing" ? "Refreshing..." : "Refresh status"}
                    </button>
                    <p className="privacy-note">
                      Stage 2 creates a queued job only. GitHub evidence ingestion and realtime
                      progress updates start in later stages.
                    </p>
                  </div>
                ) : null}
              </div>
            ) : null}
          </section>
        ) : null}

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
