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
          <span className="eyebrow subtle">1단계</span>
          <h2 id="repository-selector-title">저장소 선택</h2>
        </div>
        <label className="filter-control">
          <span>공개 범위</span>
          <select
            aria-label="저장소 공개 범위"
            value={repositoryVisibility}
            onChange={(event) => onVisibilityChange(event.target.value as RepositoryVisibility)}
          >
            <option value="all">전체</option>
            <option value="public">공개</option>
            <option value="private">비공개</option>
          </select>
        </label>
      </div>

      <p className="privacy-note">
        GitHub OAuth 세션으로 접근 가능한 저장소를 불러옵니다. 이름, 소유자 유형, 공개 범위,
        기본 브랜치, 기본 권한 같은 메타데이터만 먼저 보여줍니다.
      </p>

      {repositoryState === "loading" ? <p>접근 가능한 저장소를 불러오는 중입니다...</p> : null}
      {repositoryState === "error" ? (
        <p className="notice error">{repositoryError ?? "저장소 목록을 불러오지 못했습니다."}</p>
      ) : null}
      {repositoryState === "loaded" && repositories.length === 0 ? (
        <p className="empty-state">
          이 필터에 해당하는 저장소가 없습니다. 다른 공개 범위를 선택하거나 OAuth 권한 범위를 확인해 주세요.
        </p>
      ) : null}

      {repositories.length > 0 ? (
        <ul className="repository-list" aria-label="접근 가능한 저장소">
          {repositories.map((repository) => {
            const isSelected = selectedRepository?.id === repository.id;

            return (
              <li key={repository.id} className={isSelected ? "repository selected" : "repository"}>
                <button
                  type="button"
                  className="repository-button"
                  aria-pressed={isSelected}
                  aria-label={`${repository.full_name} 선택`}
                  onClick={() => onSelectRepository(repository)}
                >
                  <span className="repository-main">
                    <span className="repository-name">{repository.full_name}</span>
                    <span className="repository-description">
                      {repository.description ?? "설명이 없습니다."}
                    </span>
                  </span>
                  <span className="repository-meta">
                    <span className={repository.private ? "badge private" : "badge public"}>
                      {repository.private ? "비공개" : "공개"}
                    </span>
                    <span className="badge">{repository.owner_type}</span>
                    <span className="badge">기본 브랜치: {repository.default_branch}</span>
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
