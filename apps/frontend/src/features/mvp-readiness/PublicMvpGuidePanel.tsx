const readinessCards = [
  {
    eyebrow: "권한 안내",
    title: "접근 범위와 개인정보 기대치",
    description:
      "Commitfolio는 GitHub OAuth로 접근 가능한 저장소를 보여주되, 분석은 사용자가 직접 선택한 저장소 하나에 대해서만 실행합니다.",
    bullets: [
      "로그인 직후에는 저장소 메타데이터만 먼저 조회합니다.",
      "조직 저장소가 보이지 않으면 GitHub 조직의 OAuth App 승인 상태를 확인해야 합니다.",
      "세션이 만료되거나 서버가 재시작되면 다시 로그인해 토큰을 연결합니다.",
    ],
  },
  {
    eyebrow: "검증 범위",
    title: "MVP 샘플 체크리스트",
    description:
      "공개 배포 전에는 public/private/org 저장소를 최소 한 번씩 확인해 권한 안내, 빈 상태, 실패 경로가 모두 설명 가능한지 봐야 합니다.",
    bullets: [
      "public repo: 기본 happy path와 결과 생성",
      "private repo: repo scope와 세션 유지 확인",
      "org repo: 조직 승인과 접근 불가 에러 안내 확인",
    ],
  },
  {
    eyebrow: "배포 준비",
    title: "운영자가 끝까지 확인할 것",
    description:
      "Render/Vercel/Neon readiness와 env 값은 저장소 문서를 기준으로 맞추고, preview smoke 이후 public release를 진행합니다.",
    bullets: [
      "README로 local setup과 env 이름을 맞춥니다.",
      "`operator-deployment-actions.md`로 콘솔 사용자 액션을 확인합니다.",
      "preview smoke 이후 public release 체크리스트를 따라갑니다.",
    ],
  },
] as const;

export function PublicMvpGuidePanel() {
  return (
    <section className="panel guide-panel" aria-labelledby="public-mvp-guide-title">
      <div className="section-heading">
        <div>
          <span className="eyebrow subtle">Stage 9 readiness</span>
          <h2 id="public-mvp-guide-title">공개 MVP 전 체크할 것</h2>
        </div>
      </div>

      <div className="guide-grid">
        {readinessCards.map((card) => (
          <article key={card.title} className="guide-card">
            <span className="eyebrow subtle">{card.eyebrow}</span>
            <h3>{card.title}</h3>
            <p>{card.description}</p>
            <ul className="guide-list">
              {card.bullets.map((bullet) => (
                <li key={bullet}>{bullet}</li>
              ))}
            </ul>
          </article>
        ))}
      </div>

      <p className="guide-footer">
        현재 baseline은 public MVP 직전의 문서·권한 안내·실행 흐름을 정리하는 단계입니다. 실제
        Render/Vercel/Neon 배포와 GitHub OAuth 콘솔 반영은 운영자 사용자 액션으로 이어집니다.
      </p>
    </section>
  );
}
