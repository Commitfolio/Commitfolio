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
      <h3>Edit result draft</h3>
      <label>
        <span>Headline</span>
        <input value={headline} onChange={(event) => setHeadline(event.target.value)} />
      </label>
      <label>
        <span>Project overview</span>
        <textarea value={projectOverview} onChange={(event) => setProjectOverview(event.target.value)} />
      </label>
      <label>
        <span>Role summary</span>
        <textarea value={roleSummary} onChange={(event) => setRoleSummary(event.target.value)} />
      </label>
      <label>
        <span>Key contributions</span>
        <textarea value={keyContributions} onChange={(event) => setKeyContributions(event.target.value)} />
      </label>
      <label>
        <span>Tech stack</span>
        <input value={techStack} onChange={(event) => setTechStack(event.target.value)} />
      </label>
      <label>
        <span>Evidence summary</span>
        <textarea value={evidenceSummary} onChange={(event) => setEvidenceSummary(event.target.value)} />
      </label>
      <label>
        <span>Interview questions</span>
        <textarea value={interviewQuestions} onChange={(event) => setInterviewQuestions(event.target.value)} />
      </label>
      <button className="button primary" type="submit" disabled={saving}>
        {saving ? "Saving result..." : "Save result edits"}
      </button>
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
