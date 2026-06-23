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
  regeneratePortfolioResult,
  type PortfolioResultUpdateRequest,
  updatePortfolioResult,
} from "../../shared/api/commitfolio-api";

export function useResultViewer() {
  const [resultState, setResultState] = useState<ResultState>("idle");
  const [resultError, setResultError] = useState<string | null>(null);
  const [result, setResult] = useState<PortfolioResult | null>(null);
  const [recentResults, setRecentResults] = useState<PortfolioResultListItem[]>([]);
  const [savePending, setSavePending] = useState(false);
  const [regeneratePending, setRegeneratePending] = useState(false);

  async function handleGenerateResult(jobId: string) {
    setResultState("generating");
    setResultError(null);

    try {
      const generated = await generatePortfolioResult(jobId);
      setResult(generated);
      setResultState("loaded");
      await loadRecentResults();
    } catch (error) {
      setResultError(error instanceof Error ? error.message : "결과를 생성하는 중 알 수 없는 오류가 발생했습니다.");
      setResultState("error");
    }
  }

  async function loadRecentResults() {
    try {
      const response = await fetchPortfolioResults();
      setRecentResults(response.items);
    } catch {
      // 최근 결과 목록은 보조 기능이므로 실패해도 핵심 흐름은 유지한다.
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
      setResultError(error instanceof Error ? error.message : "결과를 불러오는 중 알 수 없는 오류가 발생했습니다.");
      setResultState("error");
    }
  }



  async function handleSaveResult(payload: PortfolioResultUpdateRequest) {
    if (!result) {
      return;
    }

    setSavePending(true);
    setResultError(null);

    try {
      const updated = await updatePortfolioResult(result.result_id, payload);
      setResult(updated);
      setResultState("loaded");
      await loadRecentResults();
    } catch (error) {
      setResultError(error instanceof Error ? error.message : "결과를 저장하는 중 알 수 없는 오류가 발생했습니다.");
      setResultState("error");
    } finally {
      setSavePending(false);
    }
  }

  async function handleRegenerateResult() {
    if (!result) {
      return;
    }

    setRegeneratePending(true);
    setResultError(null);

    try {
      const regenerated = await regeneratePortfolioResult(result.result_id);
      setResult(regenerated);
      setResultState("loaded");
      await loadRecentResults();
    } catch (error) {
      setResultError(error instanceof Error ? error.message : "결과를 다시 생성하는 중 알 수 없는 오류가 발생했습니다.");
      setResultState("error");
    } finally {
      setRegeneratePending(false);
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
    handleRegenerateResult,
    handleSaveResult,
    handleSelectResult,
    loadRecentResults,
    recentResults,
    regeneratePending,
    resetResult,
    result,
    resultError,
    resultState,
    savePending,
  };
}
