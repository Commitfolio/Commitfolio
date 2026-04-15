import { useEffect, useMemo, useState } from "react";
import type { AuthenticatedUser, SessionState } from "../entities/session/session.types";
import { AnalysisJobPanel } from "../features/analysis-job/AnalysisJobPanel";
import { useAnalysisJobFlow } from "../features/analysis-job/useAnalysisJobFlow";
import { getStatusMessage } from "../features/github-auth/auth-status";
import { SessionPanel } from "../features/github-auth/SessionPanel";
import { RepositorySelector } from "../features/repository-selector/RepositorySelector";
import { useRepositorySelector } from "../features/repository-selector/useRepositorySelector";
import { fetchCurrentUser, getAuthStartUrl, logout } from "../shared/api/commitfolio-api";

export default function App() {
  const [sessionState, setSessionState] = useState<SessionState>("loading");
  const [user, setUser] = useState<AuthenticatedUser | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [logoutPending, setLogoutPending] = useState(false);

  const authStartUrl = useMemo(() => getAuthStartUrl(), []);
  const statusMessage = useMemo(() => getStatusMessage(window.location.search), []);
  const analysis = useAnalysisJobFlow();
  const repositories = useRepositorySelector({
    onResetAnalysis: analysis.resetAnalysisJob,
    sessionState,
  });

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
      repositories.resetRepositories();
      analysis.resetAnalysisJob();
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
        <h1>Choose the repository to turn into a portfolio</h1>
        <p className="lede">
          Commitfolio starts with GitHub OAuth, then asks you to choose one repository. Stage 1 reads
          repository metadata only; commits, pull requests, issues, reviews, and changed files are
          collected in later analysis stages.
        </p>

        {statusMessage ? <p className="notice success">{statusMessage}</p> : null}
        {errorMessage ? <p className="notice error">{errorMessage}</p> : null}

        <SessionPanel
          authStartUrl={authStartUrl}
          logoutPending={logoutPending}
          sessionState={sessionState}
          user={user}
          onLogout={handleLogout}
        />

        {sessionState === "signed-in" ? (
          <RepositorySelector
            repositories={repositories.repositories}
            repositoryError={repositories.repositoryError}
            repositoryState={repositories.repositoryState}
            repositoryVisibility={repositories.repositoryVisibility}
            selectedRepository={repositories.selectedRepository}
            onSelectRepository={repositories.handleSelectRepository}
            onVisibilityChange={repositories.setRepositoryVisibility}
          >
            {repositories.selectedRepository ? (
              <AnalysisJobPanel
                analysisJob={analysis.analysisJob}
                analysisJobError={analysis.analysisJobError}
                analysisJobState={analysis.analysisJobState}
                evidenceError={analysis.evidenceError}
                evidenceState={analysis.evidenceState}
                evidenceSummary={analysis.evidenceSummary}
                progressEvents={analysis.progressEvents}
                progressStreamError={analysis.progressStreamError}
                progressStreamState={analysis.progressStreamState}
                selectedRepository={repositories.selectedRepository}
                onCreateAnalysisJob={() =>
                  analysis.handleCreateAnalysisJob(repositories.selectedRepository!)
                }
                onRefreshAnalysisJob={analysis.handleRefreshAnalysisJob}
                onRunAnalysisJob={analysis.handleRunAnalysisJob}
              />
            ) : null}
          </RepositorySelector>
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
