import { useEffect, useState } from "react";
import type { SessionState } from "../../entities/session/session.types";
import type { RepositoryState, RepositorySummary, RepositoryVisibility } from "../../entities/repository/repository.types";
import { fetchRepositories, lookupRepository } from "../../shared/api/commitfolio-api";

type UseRepositorySelectorOptions = {
  onResetAnalysis: () => void;
  sessionState: SessionState;
};

export function useRepositorySelector({ onResetAnalysis, sessionState }: UseRepositorySelectorOptions) {
  const [repositoryState, setRepositoryState] = useState<RepositoryState>("idle");
  const [repositoryVisibility, setRepositoryVisibility] = useState<RepositoryVisibility>("all");
  const [repositories, setRepositories] = useState<RepositorySummary[]>([]);
  const [selectedRepository, setSelectedRepository] = useState<RepositorySummary | null>(null);
  const [repositoryError, setRepositoryError] = useState<string | null>(null);
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [loadingMore, setLoadingMore] = useState(false);
  const [loadMoreError, setLoadMoreError] = useState<string | null>(null);
  const [lookupState, setLookupState] = useState<"idle" | "loading" | "error">("idle");
  const [lookupError, setLookupError] = useState<string | null>(null);

  function resetRepositories() {
    setRepositoryState("idle");
    setRepositories([]);
    setSelectedRepository(null);
    setRepositoryError(null);
    setNextCursor(null);
    setLoadingMore(false);
    setLoadMoreError(null);
    setLookupState("idle");
    setLookupError(null);
  }

  function handleSelectRepository(repository: RepositorySummary) {
    setSelectedRepository(repository);
    onResetAnalysis();
  }

  async function handleLoadMoreRepositories() {
    if (!nextCursor || loadingMore) {
      return;
    }

    setLoadingMore(true);
    setLoadMoreError(null);

    try {
      const response = await fetchRepositories(repositoryVisibility, nextCursor);
      setRepositories((current) => mergeRepositories(current, response.items));
      setNextCursor(response.next_cursor);
    } catch (error) {
      setLoadMoreError(
        error instanceof Error ? error.message : "저장소를 더 불러오는 중 알 수 없는 오류가 발생했습니다.",
      );
    } finally {
      setLoadingMore(false);
    }
  }


  async function handleLookupRepository(input: string) {
    const fullName = normalizeRepositoryInput(input);
    if (!fullName) {
      setLookupState("error");
      setLookupError("저장소 이름 또는 GitHub URL을 입력해 주세요. 예: SERVICE-MOHAENG/Mohaeng-BE");
      return;
    }

    setLookupState("loading");
    setLookupError(null);

    try {
      const repository = await lookupRepository(fullName);
      setRepositories((current) => mergeRepositories(current, [repository]));
      setSelectedRepository(repository);
      onResetAnalysis();
      setLookupState("idle");
    } catch (error) {
      setLookupError(error instanceof Error ? error.message : "저장소를 찾는 중 알 수 없는 오류가 발생했습니다.");
      setLookupState("error");
    }
  }

  useEffect(() => {
    if (sessionState !== "signed-in") {
      resetRepositories();
      onResetAnalysis();
      return;
    }

    let cancelled = false;

    async function loadRepositories() {
      setRepositoryState("loading");
      setRepositoryError(null);
      setLoadMoreError(null);
      setNextCursor(null);
      setSelectedRepository(null);
      onResetAnalysis();

      try {
        const response = await fetchRepositories(repositoryVisibility);

        if (cancelled) {
          return;
        }

        setRepositories(response.items);
        setNextCursor(response.next_cursor);
        setRepositoryState("loaded");
      } catch (error) {
        if (cancelled) {
          return;
        }

        setRepositories([]);
        setNextCursor(null);
        setRepositoryError(
          error instanceof Error ? error.message : "저장소 목록을 불러오는 중 알 수 없는 오류가 발생했습니다.",
        );
        setRepositoryState("error");
      }
    }

    void loadRepositories();

    return () => {
      cancelled = true;
    };
  }, [onResetAnalysis, repositoryVisibility, sessionState]);

  return {
    handleLoadMoreRepositories,
    handleLookupRepository,
    handleSelectRepository,
    hasMoreRepositories: Boolean(nextCursor),
    loadingMore,
    lookupError,
    lookupState,
    loadMoreError,
    repositories,
    repositoryError,
    repositoryState,
    repositoryVisibility,
    resetRepositories,
    selectedRepository,
    setRepositoryVisibility,
  };
}

function mergeRepositories(
  current: RepositorySummary[],
  nextItems: RepositorySummary[],
): RepositorySummary[] {
  const seen = new Set(current.map((repository) => repository.id));
  const merged = [...current];

  for (const repository of nextItems) {
    if (!seen.has(repository.id)) {
      merged.push(repository);
      seen.add(repository.id);
    }
  }

  return merged;
}

function normalizeRepositoryInput(value: string): string | null {
  const trimmed = value.trim();
  if (!trimmed) {
    return null;
  }

  const githubMatch = trimmed.match(/^https?:\/\/github\.com\/([^/]+)\/([^/?#]+)\/?/i);
  if (githubMatch) {
    return `${githubMatch[1]}/${githubMatch[2].replace(/\.git$/, "")}`;
  }

  const fullNameMatch = trimmed.match(/^([^/\s]+)\/([^/\s]+)$/);
  if (!fullNameMatch) {
    return null;
  }

  return `${fullNameMatch[1]}/${fullNameMatch[2].replace(/\.git$/, "")}`;
}
