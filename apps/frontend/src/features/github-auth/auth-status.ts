import { getKoreanErrorMessage } from "../../shared/api/error-messages";

export function getStatusMessage(search: string): string | null {
  const params = new URLSearchParams(search);

  if (params.get("auth") === "success") {
    return "GitHub 로그인이 완료되었습니다. 이제 저장소를 선택할 수 있습니다.";
  }

  const authError = params.get("auth_error");

  if (!authError) {
    return null;
  }

  return getKoreanErrorMessage(
    authError,
    "로그인 중 문제가 발생했습니다. 백엔드 로그를 확인한 뒤 다시 시도해 주세요.",
  );
}
