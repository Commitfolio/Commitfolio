import { useCallback, useEffect, useMemo, useState } from "react";
import type { AuthenticatedUser, SessionState } from "../entities/session/session.types";
import { AnalysisJobPanel } from "../features/analysis-job/AnalysisJobPanel";
import { useAnalysisJobFlow } from "../features/analysis-job/useAnalysisJobFlow";
import { getStatusMessage } from "../features/github-auth/auth-status";
import { SessionPanel } from "../features/github-auth/SessionPanel";
import { RepositorySelector } from "../features/repository-selector/RepositorySelector";
import { useRepositorySelector } from "../features/repository-selector/useRepositorySelector";
import { ResultEditor } from "../features/result-editor/ResultEditor";
import { RecentResults } from "../features/result-viewer/RecentResults";
import { ResultDocument } from "../features/result-viewer/ResultDocument";
import { ResultExportActions } from "../features/result-viewer/ResultExportActions";
import { useResultViewer } from "../features/result-viewer/useResultViewer";
import { fetchCurrentUser, getAuthStartUrl, logout } from "../shared/api/commitfolio-api";

export default function App() {
  const [sessionState, setSessionState] = useState<SessionState>("loading");
  const [user, setUser] = useState<AuthenticatedUser | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [logoutPending, setLogoutPending] = useState(false);

  const authStartUrl = useMemo(() => getAuthStartUrl(), []);
  const statusMessage = useMemo(() => getStatusMessage(window.location.search), []);
  const analysis = useAnalysisJobFlow();
  const results = useResultViewer();
  const resetAnalysisJob = analysis.resetAnalysisJob;
  const resetResult = results.resetResult;
  const resetAnalysisAndResult = useCallback(() => {
    resetAnalysisJob();
    resetResult();
  }, [resetAnalysisJob, resetResult]);
  const repositories = useRepositorySelector({
    onResetAnalysis: resetAnalysisAndResult,
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
          error instanceof Error ? error.message : "세션 상태를 불러오는 중 알 수 없는 오류가 발생했습니다.",
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
      resetAnalysisJob();
      resetResult();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "로그아웃에 실패했습니다.");
    } finally {
      setLogoutPending(false);
    }
  }

  function handlePrintResult() {
    window.print();
  }

  return (
    <main className="shell">
      <header className="app-header">
        <div className="brand-lockup">
          <span className="mark" aria-hidden="true">CF</span>
          <div>
            <p className="eyebrow">Commitfolio MVP</p>
            <h1>GitHub 활동을 포트폴리오 문서로 바꾸기</h1>
          </div>
        </div>
        <p className="lede">
          저장소를 선택하면 Commit, Pull Request, Issue, Review, 변경 파일 근거를 모아 편집 가능한 포트폴리오 초안을 만듭니다.
        </p>
      </header>

      <section className="workflow-strip" aria-label="작업 흐름">
        <span>1. GitHub 로그인</span>
        <span>2. 저장소 선택</span>
        <span>3. 분석 실행</span>
        <span>4. 결과 편집·PDF 저장</span>
      </section>

      <section className="card">
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
            hasMoreRepositories={repositories.hasMoreRepositories}
            loadingMore={repositories.loadingMore}
            loadMoreError={repositories.loadMoreError}
            onLoadMoreRepositories={repositories.handleLoadMoreRepositories}
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
                onGenerateResult={() => {
                  if (analysis.analysisJob) {
                    void results.handleGenerateResult(analysis.analysisJob.job_id);
                  }
                }}
                onRefreshAnalysisJob={analysis.handleRefreshAnalysisJob}
                onRunAnalysisJob={analysis.handleRunAnalysisJob}
                resultGenerationDisabled={
                  !analysis.analysisJob ||
                  analysis.analysisJob.status !== "completed" ||
                  results.resultState === "generating"
                }
                resultGenerationLabel={
                  results.resultState === "generating" ? "결과 생성 중..." : "포트폴리오 결과 생성"
                }
              />
            ) : null}
          </RepositorySelector>
        ) : null}

        {sessionState === "signed-in" ? (
          <section className="panel result-panel" aria-labelledby="result-viewer-title">
            <div className="section-heading">
              <div>
                <span className="eyebrow subtle">결과 문서</span>
                <h2 id="result-viewer-title">포트폴리오 결과</h2>
              </div>
              <button className="button secondary" type="button" onClick={() => void results.loadRecentResults()}>
                최근 결과 불러오기
              </button>
            </div>
            {results.resultError ? <p className="notice error">{results.resultError}</p> : null}
            <RecentResults items={results.recentResults} onSelectResult={results.handleSelectResult} />
            {results.result ? (
              <div className="printable-result">
                <div className="result-actions no-print">
                  <button
                    className="button secondary"
                    disabled={results.regeneratePending}
                    type="button"
                    onClick={() => void results.handleRegenerateResult()}
                  >
                    {results.regeneratePending ? "다시 생성 중..." : "결과 다시 생성"}
                  </button>
                </div>
                <ResultExportActions onPrint={handlePrintResult} />
                <ResultDocument result={results.result} />
                <div className="no-print">
                  <ResultEditor
                    result={results.result}
                    saving={results.savePending}
                    onSave={(payload) => void results.handleSaveResult(payload)}
                  />
                </div>
              </div>
            ) : (
              <p className="empty-state">
                분석을 실행한 뒤 포트폴리오 결과를 생성하면 편집 가능한 초안이 여기에 표시됩니다.
              </p>
            )}
          </section>
        ) : null}

        <div className="meta">
          <p>
            GitHub 로그인 시작 URL: <code>{authStartUrl}</code>
          </p>
          <p>
            백엔드 주소가 <code>http://localhost:8000</code>이 아니면 <code>VITE_API_BASE_URL</code>을 설정하세요.
          </p>
        </div>
      </section>
    </main>
  );
}
