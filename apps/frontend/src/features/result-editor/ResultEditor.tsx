import type { FormEvent } from "react";
import { useEffect, useState } from "react";
import type { PortfolioResult } from "../../entities/portfolio-result/portfolio-result.types";
import type { PortfolioResultUpdateRequest } from "../../shared/api/commitfolio-api";

type ResultEditorProps = {
  result: PortfolioResult;
  saving: boolean;
  onSave: (payload: PortfolioResultUpdateRequest) => void;
};

export function ResultEditor({ result, saving, onSave }: ResultEditorProps) {
  const [headline, setHeadline] = useState(result.headline);
  const [projectOverview, setProjectOverview] = useState(result.project_overview);
  const [roleSummary, setRoleSummary] = useState(result.role_summary);
  const [keyContributions, setKeyContributions] = useState(result.key_contributions.join("\n"));
  const [techStack, setTechStack] = useState(result.tech_stack.join(", "));
  const [evidenceSummary, setEvidenceSummary] = useState(result.evidence_summary);
  const [interviewQuestions, setInterviewQuestions] = useState(result.interview_questions.join("\n"));

  useEffect(() => {
    setHeadline(result.headline);
    setProjectOverview(result.project_overview);
    setRoleSummary(result.role_summary);
    setKeyContributions(result.key_contributions.join("\n"));
    setTechStack(result.tech_stack.join(", "));
    setEvidenceSummary(result.evidence_summary);
    setInterviewQuestions(result.interview_questions.join("\n"));
  }, [result]);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSave({
      headline,
      project_overview: projectOverview,
      role_summary: roleSummary,
      key_contributions: splitLines(keyContributions),
      tech_stack: splitComma(techStack),
      evidence_summary: evidenceSummary,
      interview_questions: splitLines(interviewQuestions),
    });
  }

  return (
    <form className="result-editor" onSubmit={handleSubmit}>
      <div>
        <span className="eyebrow subtle">편집</span>
        <h3>결과 직접 수정</h3>
      </div>
      <p className="privacy-note">
        초안을 그대로 두지 말고, 역할과 성과가 더 분명하게 보이도록 문장을 다듬은 뒤 저장합니다.
      </p>
      <label>
        <span>한 줄 소개</span>
        <input aria-label="한 줄 소개" value={headline} onChange={(event) => setHeadline(event.target.value)} />
      </label>
      <label>
        <span>프로젝트 개요</span>
        <textarea value={projectOverview} onChange={(event) => setProjectOverview(event.target.value)} />
      </label>
      <label>
        <span>담당 역할</span>
        <textarea value={roleSummary} onChange={(event) => setRoleSummary(event.target.value)} />
      </label>
      <label>
        <span>핵심 기여</span>
        <textarea value={keyContributions} onChange={(event) => setKeyContributions(event.target.value)} />
      </label>
      <label>
        <span>기술 스택</span>
        <input value={techStack} onChange={(event) => setTechStack(event.target.value)} />
      </label>
      <label>
        <span>활동·근거 요약</span>
        <textarea value={evidenceSummary} onChange={(event) => setEvidenceSummary(event.target.value)} />
      </label>
      <label>
        <span>면접 예상 질문</span>
        <textarea value={interviewQuestions} onChange={(event) => setInterviewQuestions(event.target.value)} />
      </label>
      <div className="action-row">
        <button className="button primary" type="submit" disabled={saving}>
          {saving ? "저장 중..." : "수정 내용 저장"}
        </button>
      </div>
    </form>
  );
}

function splitLines(value: string): string[] {
  return value
    .split("\n")
    .map((item) => item.trim())
    .filter(Boolean);
}

function splitComma(value: string): string[] {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}
