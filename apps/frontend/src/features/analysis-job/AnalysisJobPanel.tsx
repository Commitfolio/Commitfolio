import type {
  AnalysisJob,
  AnalysisJobEvent,
  AnalysisJobState,
  EvidenceState,
  EvidenceSummary,
  ProgressStreamState,
} from "../../entities/analysis-job/analysis-job.types";
import type { RepositorySummary } from "../../entities/repository/repository.types";

type AnalysisJobPanelProps = {
  analysisJob: AnalysisJob | null;
  analysisJobError: string | null;
  analysisJobState: AnalysisJobState;
  evidenceError: string | null;
  evidenceState: EvidenceState;
  evidenceSummary: EvidenceSummary | null;
  progressEvents: AnalysisJobEvent[];
  progressStreamError: string | null;
  progressStreamState: ProgressStreamState;
  selectedRepository: RepositorySummary;
  onCreateAnalysisJob: () => void;
  onRefreshAnalysisJob: () => void;
  onGenerateResult: () => void;
  onRunAnalysisJob: () => void;
  resultGenerationDisabled: boolean;
  resultGenerationLabel: string;
};

export function AnalysisJobPanel({
  analysisJob,
  analysisJobError,
  analysisJobState,
  evidenceError,
  evidenceState,
  evidenceSummary,
  progressEvents,
  progressStreamError,
  progressStreamState,
  selectedRepository,
  onCreateAnalysisJob,
  onGenerateResult,
  onRefreshAnalysisJob,
  onRunAnalysisJob,
  resultGenerationDisabled,
  resultGenerationLabel,
}: AnalysisJobPanelProps) {
  const visibleEvents = progressEvents.length > 0 ? progressEvents : evidenceSummary?.latest_events ?? [];
  const canGenerateResult = !resultGenerationDisabled;
  const runButtonClassName = canGenerateResult ? "button secondary" : "button primary";
  const generateButtonClassName = canGenerateResult ? "button primary" : "button secondary";

  return (
    <div className="selected-repository">
      <div className="panel-intro compact">
        <div>
          <span className="eyebrow subtle">선택됨</span>
          <p className="selection-title">
            <strong>{selectedRepository.full_name}</strong> 저장소로 분석 작업을 만들 수 있습니다.
          </p>
        </div>
        <div className="action-row">
          <button
            className="button primary"
            disabled={analysisJobState === "creating"}
            onClick={onCreateAnalysisJob}
            type="button"
          >
            {analysisJobState === "creating" ? "분석 작업 생성 중..." : "분석 작업 만들기"}
          </button>
          <a className="button tertiary" href={selectedRepository.html_url} target="_blank" rel="noreferrer">
            GitHub 저장소 보기
          </a>
        </div>
      </div>

      {analysisJobError ? <p className="notice error">{analysisJobError}</p> : null}

      {analysisJob ? (
        <div className="job-summary">
          <div>
            <span className="eyebrow subtle">분석 작업</span>
            <h3>{analysisJob.job_id}</h3>
          </div>
          <dl className="user-grid">
            <div>
              <dt>상태</dt>
              <dd>{getJobStatusLabel(analysisJob.status)}</dd>
            </div>
            <div>
              <dt>저장소</dt>
              <dd>{analysisJob.repository_full_name}</dd>
            </div>
            <div>
              <dt>브랜치</dt>
              <dd>{analysisJob.branch}</dd>
            </div>
            <div>
              <dt>진행률</dt>
              <dd>
                {analysisJob.progress.stage} · {analysisJob.progress.percent}%
              </dd>
            </div>
          </dl>
          <div className="progress-meter" aria-hidden="true">
            <span style={{ width: `${analysisJob.progress.percent}%` }} />
          </div>
          <p className="action-note">
            {canGenerateResult
              ? "분석이 끝났습니다. 이제 포트폴리오 결과 생성을 진행하면 됩니다."
              : "아직 결과 생성 전 단계입니다. 상태를 확인하거나 분석을 실행해 다음 단계로 진행합니다."}
          </p>
          {analysisJob.failure_reason ? <p className="notice error">{analysisJob.failure_reason}</p> : null}
          <div className="action-row">
            <button
              className="button tertiary"
              disabled={analysisJobState === "refreshing"}
              onClick={onRefreshAnalysisJob}
              type="button"
            >
              {analysisJobState === "refreshing" ? "상태 새로고침 중..." : "상태 새로고침"}
            </button>
            <button
              className={runButtonClassName}
              disabled={evidenceState === "running"}
              onClick={onRunAnalysisJob}
              type="button"
            >
              {evidenceState === "running" ? "분석 실행 중..." : "분석 실행"}
            </button>
            <button
              className={generateButtonClassName}
              disabled={resultGenerationDisabled}
              onClick={onGenerateResult}
              type="button"
            >
              {resultGenerationLabel}
            </button>
          </div>
          <div className="stream-status" aria-live="polite">
            진행 스트림: {getStreamStateLabel(progressStreamState)}
          </div>
          {progressStreamError ? <p className="notice error">{progressStreamError}</p> : null}
          {evidenceError ? <p className="notice error">{evidenceError}</p> : null}
          {evidenceSummary ? (
            <div className="evidence-summary">
              <div>
                <span className="eyebrow subtle">분석 근거</span>
                <h3>{evidenceSummary.total_count}개 수집됨</h3>
              </div>
              <dl className="user-grid">
                {Object.entries(evidenceSummary.counts).map(([sourceType, count]) => (
                  <div key={sourceType}>
                    <dt>{getEvidenceTypeLabel(sourceType)}</dt>
                    <dd>{count}</dd>
                  </div>
                ))}
              </dl>
              {visibleEvents.length > 0 ? (
                <ul className="event-list" aria-label="최근 분석 이벤트">
                  {visibleEvents.map((event) => (
                    <li key={event.sequence}>
                      <strong>#{event.sequence}</strong> {event.message}
                    </li>
                  ))}
                </ul>
              ) : null}
            </div>
          ) : null}
          <p className="privacy-note">
            진행 상황은 서버의 durable event log에서 재생됩니다. 연결이 끊겨도 상태 새로고침으로 복구할 수 있습니다.
          </p>
        </div>
      ) : null}
    </div>
  );
}

function getJobStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    queued: "대기 중",
    running: "실행 중",
    completed: "완료",
    failed: "실패",
  };
  return labels[status] ?? status;
}

function getStreamStateLabel(status: ProgressStreamState): string {
  const labels: Record<ProgressStreamState, string> = {
    idle: "대기",
    connecting: "연결 중",
    streaming: "수신 중",
    unsupported: "지원 안 됨",
    closed: "종료됨",
    error: "오류",
  };
  return labels[status];
}

function getEvidenceTypeLabel(sourceType: string): string {
  const labels: Record<string, string> = {
    commit: "커밋",
    pull_request: "Pull Request",
    issue: "Issue",
    review: "Review",
    changed_file: "변경 파일",
  };
  return labels[sourceType] ?? sourceType;
}
