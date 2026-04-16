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
      <h2>로그인 상태</h2>
      {sessionState === "loading" ? <p>현재 세션을 확인하는 중입니다...</p> : null}

      {sessionState === "signed-out" ? (
        <>
          <p>아직 로그인하지 않았습니다. GitHub 계정으로 연결하면 접근 가능한 저장소를 불러올 수 있습니다.</p>
          <a className="button primary" href={authStartUrl}>
            GitHub로 계속하기
          </a>
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
          <button className="button secondary" disabled={logoutPending} onClick={onLogout}>
            {logoutPending ? "로그아웃 중..." : "로그아웃"}
          </button>
        </>
      ) : null}
    </div>
  );
}
