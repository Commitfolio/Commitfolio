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
          <button className="button secondary" disabled={logoutPending} onClick={onLogout}>
            {logoutPending ? "Signing out..." : "Log out"}
          </button>
        </>
      ) : null}
    </div>
  );
}
