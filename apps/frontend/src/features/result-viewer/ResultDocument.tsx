import type { ReactNode } from "react";
import type { PortfolioResult } from "../../entities/portfolio-result/portfolio-result.types";

type ResultDocumentProps = {
  result: PortfolioResult;
};

export function ResultDocument({ result }: ResultDocumentProps) {
  const summaryCards = [
    {
      label: "대표 기술",
      value: result.tech_stack.slice(0, 4).join(" · ") || "기술 추론 없음",
    },
    {
      label: "핵심 기여",
      value: `${result.key_contributions.length}개 포인트`,
    },
    {
      label: "근거 링크",
      value: `${result.evidence_links.length}개 연결`,
    },
  ];

  return (
    <article className="result-document" aria-labelledby="portfolio-result-title">
      <div>
        <span className="eyebrow subtle">포트폴리오 결과</span>
        <h2 id="portfolio-result-title">{result.headline}</h2>
        <div className="result-summary-badges">
          <span className="badge subtle">{result.repository_full_name}</span>
          <span className="badge">version {result.version}</span>
          <span className={`badge ${getEnhancementBadgeClass(result.enhancement_status)}`}>
            {getEnhancementLabel(result.enhancement_status, result.enhancement_message)}
          </span>
          {result.enhancement_model ? <span className="badge">모델: {result.enhancement_model}</span> : null}
        </div>
      </div>

      <div className="result-highlight-grid" aria-label="결과 요약">
        {summaryCards.map((card) => (
          <div className="result-highlight-card" key={card.label}>
            <span>{card.label}</span>
            <strong>{card.value}</strong>
          </div>
        ))}
      </div>

      <section className="result-lead">
        <span className="eyebrow subtle">역할 요약</span>
        <p>{result.role_summary}</p>
      </section>

      <ResultSection title="프로젝트 개요" sectionKey="project_overview" result={result}>
        <p>{result.project_overview}</p>
      </ResultSection>

      <ResultSection title="핵심 기여" sectionKey="key_contributions" result={result}>
        <ul className="result-list">
          {result.key_contributions.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </ResultSection>

      <ResultSection title="사용 기술" sectionKey="tech_stack" result={result}>
        <div className="repository-meta">
          {result.tech_stack.map((item) => (
            <span className="badge" key={item}>{item}</span>
          ))}
        </div>
      </ResultSection>

      <ResultSection title="활동·근거 요약" sectionKey="evidence_summary" result={result}>
        <p>{result.evidence_summary}</p>
      </ResultSection>

      <ResultSection title="면접 예상 질문" sectionKey="interview_questions" result={result}>
        <ul className="result-list">
          {result.interview_questions.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </ResultSection>
    </article>
  );
}

function getEnhancementLabel(status: string | undefined, message: string | undefined): string {
  if (message) {
    return message;
  }

  if (status === "enhanced") {
    return "OpenAI 후처리 적용";
  }

  if (status === "fallback") {
    return "OpenAI 후처리 실패, 기본 생성 사용";
  }

  return "기본 생성 사용";
}

function getEnhancementBadgeClass(status: string | undefined): string {
  if (status === "enhanced") {
    return "success";
  }

  if (status === "fallback") {
    return "warning";
  }

  return "subtle";
}

type ResultSectionProps = {
  children: ReactNode;
  result: PortfolioResult;
  sectionKey: string;
  title: string;
};

function ResultSection({ children, result, sectionKey, title }: ResultSectionProps) {
  const links = result.evidence_links.filter((link) => link.section_key === sectionKey);

  return (
    <section className="result-section">
      <h3>{title}</h3>
      {children}
      {links.length > 0 ? (
        <ul className="evidence-link-list" aria-label={`${title} evidence links`}>
          {links.map((link) => (
            <li key={`${link.evidence_id}-${link.section_key}`}>
              <a href={link.url} target="_blank" rel="noreferrer">
                {link.label}
              </a>
            </li>
          ))}
        </ul>
      ) : null}
    </section>
  );
}
