import type { ReactNode } from "react";
import type {
  RepositoryState,
  RepositorySummary,
  RepositoryVisibility,
} from "../../entities/repository/repository.types";

type RepositorySelectorProps = {
  repositories: RepositorySummary[];
  repositoryError: string | null;
  repositoryState: RepositoryState;
  repositoryVisibility: RepositoryVisibility;
  selectedRepository: RepositorySummary | null;
  onSelectRepository: (repository: RepositorySummary) => void;
  onVisibilityChange: (visibility: RepositoryVisibility) => void;
  children?: ReactNode;
};

export function RepositorySelector({
  repositories,
  repositoryError,
  repositoryState,
  repositoryVisibility,
  selectedRepository,
  onSelectRepository,
  onVisibilityChange,
  children,
}: RepositorySelectorProps) {
  return (
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
            onChange={(event) => onVisibilityChange(event.target.value as RepositoryVisibility)}
          >
            <option value="all">All</option>
            <option value="public">Public</option>
            <option value="private">Private</option>
          </select>
        </label>
      </div>

      <p className="privacy-note">
        We list repositories available to your GitHub OAuth session so you can choose one project.
        This step shows metadata such as name, owner type, visibility, default branch, and basic
        permissions.
      </p>

      {repositoryState === "loading" ? <p>Loading accessible repositories...</p> : null}
      {repositoryState === "error" ? (
        <p className="notice error">{repositoryError ?? "Failed to load repositories."}</p>
      ) : null}
      {repositoryState === "loaded" && repositories.length === 0 ? (
        <p className="empty-state">
          No repositories were returned for this visibility filter. Try a different filter or confirm
          the OAuth app has the repository scopes you expect.
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
                  onClick={() => onSelectRepository(repository)}
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

      {children}
    </section>
  );
}
