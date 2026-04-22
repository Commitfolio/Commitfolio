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
          <p>
            아직 로그인하지 않았습니다. GitHub 계정으로 연결하면 접근 가능한 public/private/org
            저장소를 불러올 수 있습니다.
          </p>
          <p className="privacy-note">
            조직 저장소가 보이지 않으면 GitHub 조직의 OAuth App 승인 상태를 확인해 주세요. 로그인
            직후에는 저장소 메타데이터만 조회하고, 분석은 사용자가 선택한 저장소 하나에 대해서만
            실행합니다.
          </p>
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
          <p className="privacy-note">
            현재 세션은 GitHub OAuth 쿠키로 유지됩니다. 분석은 선택한 저장소 하나에 대해서만
            수행하고, 로그아웃하면 세션과 서버 메모리 토큰 연결이 함께 정리됩니다.
          </p>
          <button className="button secondary" disabled={logoutPending} onClick={onLogout}>
            {logoutPending ? "로그아웃 중..." : "로그아웃"}
          </button>
        </>
      ) : null}
    </div>
  );
}
