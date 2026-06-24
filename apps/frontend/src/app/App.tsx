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
  const isSignedIn = sessionState === "signed-in";
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
        const fallbackMessage = "세션 상태를 불러오는 중 알 수 없는 오류가 발생했습니다.";
        const message =
          error instanceof Error && error.message && error.message !== "Failed to fetch"
            ? error.message
            : fallbackMessage;
        setErrorMessage(message);
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

  const resultGenerationPending =
    results.resultState === "generating" || results.resultState === "rendering";

  const resultGenerationLabel =
    results.resultState === "rendering"
      ? "결과 정리 중..."
      : results.resultState === "generating"
        ? "결과 생성 중..."
        : "포트폴리오 결과 생성";

  return (
    <main className="shell">
      <nav className="topbar" aria-label="Commitfolio navigation">
        <a className="topbar-brand" href="/" aria-label="Commitfolio 홈">
          <span className="mark" aria-hidden="true">CF</span>
          <span>Commitfolio</span>
        </a>
        <div className="topbar-links" aria-label="제품 흐름">
          <a href="#repository-selector-title">저장소</a>
          <a href="#result-viewer-title">결과 문서</a>
          <span className={`session-chip ${isSignedIn ? "active" : ""}`}>
            {isSignedIn ? "Connected" : "Preview"}
          </span>
        </div>
      </nav>

      <header className="app-header">
        <div className="hero-copy">
          <p className="eyebrow">Architectural Portfolio Generator</p>
          <h1>GitHub 활동을 근거가 살아있는 포트폴리오 문서로 바꾸기</h1>
          <p className="lede">
            저장소를 선택하면 Commit, Pull Request, Issue, Review, 변경 파일 근거를 큐레이션해 편집 가능한 포트폴리오 초안을 만듭니다.
          </p>
          <div className="hero-support">
            <div className="hero-cta-row">
              {isSignedIn ? (
                <a className="button primary" href="#repository-selector-title">
                  저장소 선택으로 이동
                </a>
              ) : (
                <a className="button primary" href={authStartUrl}>
                  GitHub 연결 시작
                </a>
              )}
              <a
                className="button tertiary"
                href={isSignedIn ? "#result-viewer-title" : "#repository-selector-title"}
              >
                {isSignedIn ? "결과 영역 보기" : "흐름 먼저 보기"}
              </a>
            </div>
            <p className="hero-support-text">
              {isSignedIn
                ? "연결이 끝났다면 저장소 선택부터 분석 실행, 결과 생성까지 순서대로 진행하면 됩니다."
                : "첫 단계는 GitHub 연결입니다. 연결 후 접근 가능한 저장소만 불러오고, 분석은 선택한 저장소 하나에 대해서만 실행합니다."}
            </p>
          </div>
          <div className="hero-actions" aria-label="핵심 가치">
            <span className="badge subtle">Evidence-backed</span>
            <span className="badge subtle">Editorial document</span>
            <span className="badge subtle">PDF-ready</span>
          </div>
        </div>
        <aside className="hero-preview" aria-label="Commitfolio 포트폴리오 미리보기">
          <div className="preview-header">
            <div>
              <span className="eyebrow subtle">Commit Stream</span>
              <h2>Impact timeline</h2>
            </div>
            <span className="session-chip active">Active</span>
          </div>
          <ol className="preview-stream">
            <li>
              <span>PR #42</span>
              <strong>분산 이벤트 수집 파이프라인 안정화</strong>
              <p>latency 15% 개선 근거를 포트폴리오 섹션에 연결합니다.</p>
            </li>
            <li>
              <span>Commit 7f2d1e</span>
              <strong>Evidence link 자동 매핑</strong>
              <p>각 주장 옆에 GitHub 원문 링크를 남겨 검증 가능성을 높입니다.</p>
            </li>
            <li>
              <span>Review note</span>
              <strong>면접 질문 생성 준비</strong>
              <p>역할, 기여, 기술 판단을 질문/답변 소재로 재구성합니다.</p>
            </li>
          </ol>
        </aside>
      </header>

      <section className="workflow-strip" aria-label="작업 흐름">
        <article className="workflow-card">
          <strong>1. GitHub 로그인</strong>
          <p>접근 가능한 저장소 범위를 연결합니다.</p>
        </article>
        <article className="workflow-card">
          <strong>2. 저장소 선택</strong>
          <p>포트폴리오로 바꿀 저장소 하나를 고릅니다.</p>
        </article>
        <article className="workflow-card">
          <strong>3. 분석 실행</strong>
          <p>진행률과 수집 근거를 확인합니다.</p>
        </article>
        <article className="workflow-card">
          <strong>4. 결과 편집·PDF 저장</strong>
          <p>문장을 다듬고 문서 형태로 내보냅니다.</p>
        </article>
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

        {isSignedIn ? (
          <RepositorySelector
            repositories={repositories.repositories}
            repositoryError={repositories.repositoryError}
            repositoryState={repositories.repositoryState}
            repositoryVisibility={repositories.repositoryVisibility}
            selectedRepository={repositories.selectedRepository}
            hasMoreRepositories={repositories.hasMoreRepositories}
            loadingMore={repositories.loadingMore}
            loadMoreError={repositories.loadMoreError}
            lookupError={repositories.lookupError}
            lookupState={repositories.lookupState}
            lookupSuccess={repositories.lookupSuccess}
            highlightedRepositoryId={repositories.highlightedRepositoryId}
            onLoadMoreRepositories={repositories.handleLoadMoreRepositories}
            onLookupRepository={repositories.handleLookupRepository}
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
                  resultGenerationPending
                }
                resultGenerationLabel={resultGenerationLabel}
              />
            ) : null}
          </RepositorySelector>
        ) : null}

        {isSignedIn ? (
          <section className="panel result-panel" aria-labelledby="result-viewer-title">
            <div className="section-heading">
              <div>
                <span className="eyebrow subtle">결과 문서</span>
                <h2 id="result-viewer-title">포트폴리오 결과</h2>
              </div>
              <button className="button tertiary" type="button" onClick={() => void results.loadRecentResults()}>
                최근 결과 불러오기
              </button>
            </div>
            {results.resultError ? <p className="notice error">{results.resultError}</p> : null}
            <RecentResults items={results.recentResults} onSelectResult={results.handleSelectResult} />
            {results.resultState === "generating" && !results.result ? (
              <p className="notice subtle">
                분석 결과를 생성하고 있습니다. 근거를 모아 포트폴리오 문서를 준비하는 중입니다.
              </p>
            ) : null}
            {results.resultState === "rendering" ? (
              <div className="notice subtle" aria-live="polite">
                분석 근거를 포트폴리오 문서로 정리하는 중입니다. 약 5초 뒤 결과를 보여줍니다.
              </div>
            ) : null}
            {results.result ? (
              <div className="printable-result">
                <div className="result-actions no-print">
                  <button
                    className="button secondary"
                    disabled={results.regeneratePending}
                    type="button"
                    onClick={() => void results.handleRegenerateResult()}
                  >
                    {results.regeneratePending ? "결과 정리 중..." : "결과 다시 생성"}
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

        {import.meta.env.DEV ? (
          <div className="meta">
            <p>
              GitHub 로그인 시작 URL: <code>{authStartUrl}</code>
            </p>
            <p>
              백엔드 주소가 <code>http://localhost:8000</code>이 아니면 <code>VITE_API_BASE_URL</code>을 설정하세요.
            </p>
          </div>
        ) : null}
      </section>
    </main>
  );
}
