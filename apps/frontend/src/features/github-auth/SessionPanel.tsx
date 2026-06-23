import type { AuthenticatedUser, SessionState } from "../../entities/session/session.types";

type SessionPanelProps = {
  authStartUrl: string;
  logoutPending: boolean;
  sessionState: SessionState;
  user: AuthenticatedUser | null;
  onLogout: () => void;
};

export function SessionPanel({
  authStartUrl,
  logoutPending,
  sessionState,
  user,
  onLogout,
}: SessionPanelProps) {
  return (
    <div className="panel">
      <div className="panel-intro">
        <div>
          <span className="eyebrow subtle">시작하기</span>
          <h2>로그인 상태</h2>
        </div>
        <p className="privacy-note">
          GitHub 연결이 끝나면 저장소 선택부터 결과 편집까지 한 화면에서 이어서 진행할 수 있습니다.
        </p>
      </div>
      {sessionState === "loading" ? <p>현재 세션을 확인하는 중입니다...</p> : null}

      {sessionState === "signed-out" ? (
        <>
          <div className="support-grid">
            <article className="support-card support-card-emphasis">
              <h3>GitHub 계정 연결</h3>
              <p>아직 로그인하지 않았습니다. GitHub 계정으로 연결하면 접근 가능한 저장소를 불러올 수 있습니다.</p>
              <div className="action-row">
                <a className="button primary" href={authStartUrl}>
                  GitHub로 계속하기
                </a>
                <a className="button tertiary" href="#repository-selector-title">
                  흐름 먼저 보기
                </a>
              </div>
            </article>
            <article className="support-card">
              <h3>연결 후 가능한 것</h3>
              <ul className="support-list">
                <li>접근 가능한 저장소 목록 조회</li>
                <li>선택한 저장소 하나만 분석 실행</li>
                <li>결과 편집 후 PDF 저장</li>
              </ul>
            </article>
          </div>
        </>
      ) : null}

      {sessionState === "signed-in" && user ? (
        <>
          <dl className="user-grid">
            <div>
              <dt>GitHub 계정</dt>
              <dd>@{user.github_login}</dd>
            </div>
            <div>
              <dt>사용자 ID</dt>
              <dd>{user.id}</dd>
            </div>
            <div>
              <dt>이름</dt>
              <dd>{user.name ?? "제공되지 않음"}</dd>
            </div>
            <div>
              <dt>연결 상태</dt>
              <dd>{user.connected ? "연결됨" : "연결 안 됨"}</dd>
            </div>
          </dl>
          <div className="support-card support-card-emphasis">
            <h3>다음 단계</h3>
            <p>이제 저장소를 하나 선택하고 분석 작업을 만들면 결과 문서 생성까지 같은 흐름으로 이어집니다.</p>
            <div className="action-row">
              <a className="button primary" href="#repository-selector-title">
                저장소 선택으로 이동
              </a>
              <button className="button danger" disabled={logoutPending} onClick={onLogout}>
                {logoutPending ? "로그아웃 중..." : "로그아웃"}
              </button>
            </div>
          </div>
        </>
      ) : null}
    </div>
  );
}
