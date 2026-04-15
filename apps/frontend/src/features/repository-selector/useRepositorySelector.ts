import { useEffect, useState } from "react";
import type { SessionState } from "../../entities/session/session.types";
import type { RepositoryState, RepositorySummary, RepositoryVisibility } from "../../entities/repository/repository.types";
import { fetchRepositories } from "../../shared/api/commitfolio-api";

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

  function resetRepositories() {
    setRepositoryState("idle");
    setRepositories([]);
    setSelectedRepository(null);
    setRepositoryError(null);
  }

  function handleSelectRepository(repository: RepositorySummary) {
    setSelectedRepository(repository);
    onResetAnalysis();
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
      setSelectedRepository(null);
      onResetAnalysis();

      try {
        const response = await fetchRepositories(repositoryVisibility);

        if (cancelled) {
          return;
        }

        setRepositories(response.items);
        setRepositoryState("loaded");
      } catch (error) {
        if (cancelled) {
          return;
        }

        setRepositories([]);
        setRepositoryError(
          error instanceof Error ? error.message : "Unknown error while loading repositories.",
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
    handleSelectRepository,
    repositories,
    repositoryError,
    repositoryState,
    repositoryVisibility,
    resetRepositories,
    selectedRepository,
    setRepositoryVisibility,
  };
}
