const ERROR_MESSAGES: Record<string, string> = {
  unauthenticated: "로그인이 필요합니다. GitHub로 다시 로그인해 주세요.",
  backend_not_configured: "백엔드 GitHub OAuth 환경변수가 아직 설정되지 않았습니다. GITHUB_CLIENT_ID와 GITHUB_CLIENT_SECRET을 확인해 주세요.",
  invalid_state: "GitHub 로그인 보안 상태값이 맞지 않습니다. 다시 로그인해 주세요.",
  missing_code: "GitHub가 인증 코드를 보내지 않았습니다. 다시 로그인해 주세요.",
  access_denied: "GitHub 로그인이 취소되었거나 거부되었습니다.",
  oauth_exchange_failed: "GitHub 토큰 교환에 실패했습니다. 백엔드 OAuth 설정을 확인해 주세요.",
  oauth_profile_failed: "GitHub 사용자 정보를 가져오지 못했습니다. 잠시 후 다시 시도해 주세요.",
  repository_lookup_failed: "저장소 목록을 가져오지 못했습니다. 권한 범위와 GitHub 상태를 확인해 주세요.",
  analysis_job_not_found: "분석 작업을 찾을 수 없습니다. 저장소를 다시 선택해 주세요.",
  analysis_job_result_not_available: "완료된 분석 작업을 찾을 수 없어 결과를 만들 수 없습니다.",
  portfolio_result_not_found: "포트폴리오 결과를 찾을 수 없습니다.",
  internal_server_error: "서버에서 예상하지 못한 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.",
};

export function getKoreanErrorMessage(code: string | undefined, fallback: string): string {
  if (!code) {
    return fallback;
  }

  return ERROR_MESSAGES[code] ?? fallback;
}
