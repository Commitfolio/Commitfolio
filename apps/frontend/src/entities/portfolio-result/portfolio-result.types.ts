export type PortfolioEvidenceLink = {
  section_key: string;
  label: string;
  url: string;
  evidence_id: string;
};

export type PortfolioResult = {
  result_id: string;
  analysis_job_id: string;
  repository_full_name: string;
  version: number;
  headline: string;
  project_overview: string;
  role_summary: string;
  key_contributions: string[];
  tech_stack: string[];
  evidence_summary: string;
  interview_questions: string[];
  evidence_links: PortfolioEvidenceLink[];
  created_at: string;
  updated_at: string;
};

export type PortfolioResultListItem = {
  result_id: string;
  analysis_job_id: string;
  repository_full_name: string;
  headline: string;
  version: number;
  created_at: string;
  updated_at: string;
};

export type PortfolioResultList = {
  items: PortfolioResultListItem[];
};

export type ResultState = "idle" | "generating" | "loaded" | "error";
