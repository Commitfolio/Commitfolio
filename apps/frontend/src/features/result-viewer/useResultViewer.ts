import { useCallback, useState } from "react";
import type {
  PortfolioResult,
  PortfolioResultListItem,
  ResultState,
} from "../../entities/portfolio-result/portfolio-result.types";
import {
  fetchPortfolioResult,
  fetchPortfolioResults,
  generatePortfolioResult,
} from "../../shared/api/commitfolio-api";

export function useResultViewer() {
  const [resultState, setResultState] = useState<ResultState>("idle");
  const [resultError, setResultError] = useState<string | null>(null);
  const [result, setResult] = useState<PortfolioResult | null>(null);
  const [recentResults, setRecentResults] = useState<PortfolioResultListItem[]>([]);

  async function handleGenerateResult(jobId: string) {
    setResultState("generating");
    setResultError(null);

    try {
      const generated = await generatePortfolioResult(jobId);
      setResult(generated);
      setResultState("loaded");
      await loadRecentResults();
    } catch (error) {
      setResultError(error instanceof Error ? error.message : "Unknown error while generating result.");
      setResultState("error");
    }
  }

  async function loadRecentResults() {
    try {
      const response = await fetchPortfolioResults();
      setRecentResults(response.items);
    } catch {
      // Recent results are supplemental; keep the main flow usable if listing fails.
    }
  }

  async function handleSelectResult(resultId: string) {
    setResultState("generating");
    setResultError(null);

    try {
      const selected = await fetchPortfolioResult(resultId);
      setResult(selected);
      setResultState("loaded");
    } catch (error) {
      setResultError(error instanceof Error ? error.message : "Unknown error while loading result.");
      setResultState("error");
    }
  }

  const resetResult = useCallback(() => {
    setResultState("idle");
    setResultError(null);
    setResult(null);
    setRecentResults([]);
  }, []);

  return {
    handleGenerateResult,
    handleSelectResult,
    loadRecentResults,
    recentResults,
    resetResult,
    result,
    resultError,
    resultState,
  };
}
