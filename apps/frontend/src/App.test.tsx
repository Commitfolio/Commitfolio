import { act, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import App from "./App";

const originalFetch = global.fetch;

class FakeEventSource {
  static instances: FakeEventSource[] = [];

  readonly url: string;
  readonly withCredentials: boolean;
  onopen: ((event: Event) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;
  private listeners: Record<string, Array<(event: MessageEvent<string>) => void>> = {};

  constructor(url: string, init?: EventSourceInit) {
    this.url = url;
    this.withCredentials = Boolean(init?.withCredentials);
    FakeEventSource.instances.push(this);
  }

  addEventListener(type: string, listener: (event: MessageEvent<string>) => void) {
    this.listeners[type] = [...(this.listeners[type] ?? []), listener];
  }

  close = vi.fn();

  emit(type: string, payload: unknown) {
    for (const listener of this.listeners[type] ?? []) {
      listener({ data: JSON.stringify(payload) } as MessageEvent<string>);
    }
  }
}

function mockFetchSequence(...responses: Array<Partial<Response>>) {
  global.fetch = vi.fn().mockImplementation(async () => {
    const response = responses.shift();

    if (!response) {
      throw new Error("Unexpected fetch call");
    }

    return {
      ok: false,
      status: 500,
      json: async () => ({}),
      ...response,
    } satisfies Partial<Response>;
  }) as typeof fetch;
}

describe("App", () => {
  afterEach(() => {
    global.fetch = originalFetch;
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
    FakeEventSource.instances = [];
    sessionStorage.clear();
    window.history.replaceState({}, "", "/");
  });

  it("shows the signed-out state when the backend reports 401", async () => {
    mockFetchSequence({ status: 401, ok: false });

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("Continue with GitHub")).toBeInTheDocument();
    });
  });

  it("renders the signed-in user details", async () => {
    mockFetchSequence({
      status: 200,
      ok: true,
      json: async () => ({
        id: "github:123",
        github_login: "octocat",
        connected: true,
        name: "The Octocat",
        avatar_url: null,
      }),
    }, {
      status: 200,
      ok: true,
      json: async () => ({
        items: [],
        next_cursor: null,
      }),
    });

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("@octocat")).toBeInTheDocument();
    });
  });

  it("logs the user out and returns to the signed-out state", async () => {
    mockFetchSequence(
      {
        status: 200,
        ok: true,
        json: async () => ({
          id: "github:123",
          github_login: "octocat",
          connected: true,
          name: "The Octocat",
          avatar_url: null,
        }),
      },
      {
        status: 200,
        ok: true,
        json: async () => ({
          items: [],
          next_cursor: null,
        }),
      },
      { status: 204, ok: true },
    );

    render(<App />);

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Log out" })).toBeInTheDocument();
    });

    await userEvent.click(screen.getByRole("button", { name: "Log out" }));

    await waitFor(() => {
      expect(screen.getByText("Continue with GitHub")).toBeInTheDocument();
    });
  });

  it("renders repositories and lets the user select one", async () => {
    mockFetchSequence(
      {
        status: 200,
        ok: true,
        json: async () => ({
          id: "github:123",
          github_login: "octocat",
          connected: true,
          name: "The Octocat",
          avatar_url: null,
        }),
      },
      {
        status: 200,
        ok: true,
        json: async () => ({
          items: [
            {
              id: 456,
              full_name: "octocat/commitfolio",
              private: true,
              owner_type: "Organization",
              default_branch: "main",
              permissions: { admin: false, push: true, pull: true },
              html_url: "https://github.com/octocat/commitfolio",
              description: "Portfolio generator",
              updated_at: "2026-04-15T00:00:00Z",
            },
          ],
          next_cursor: null,
        }),
      },
    );

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("octocat/commitfolio")).toBeInTheDocument();
    });

    await userEvent.click(screen.getByRole("button", { name: "Select octocat/commitfolio" }));

    expect(
      screen.getByText(/is ready for the next Stage 2 analysis job bootstrap/i),
    ).toBeInTheDocument();
  });

  it("creates an analysis job for the selected repository", async () => {
    mockFetchSequence(
      {
        status: 200,
        ok: true,
        json: async () => ({
          id: "github:123",
          github_login: "octocat",
          connected: true,
          name: "The Octocat",
          avatar_url: null,
        }),
      },
      {
        status: 200,
        ok: true,
        json: async () => ({
          items: [
            {
              id: 456,
              full_name: "octocat/commitfolio",
              private: true,
              owner_type: "Organization",
              default_branch: "main",
              permissions: { admin: false, push: true, pull: true },
              html_url: "https://github.com/octocat/commitfolio",
              description: "Portfolio generator",
              updated_at: "2026-04-15T00:00:00Z",
            },
          ],
          next_cursor: null,
        }),
      },
      {
        status: 201,
        ok: true,
        json: async () => ({
          job_id: "job_123",
          status: "queued",
          repository_full_name: "octocat/commitfolio",
          branch: "main",
          progress: { stage: "queued", percent: 0 },
          result_id: null,
          failure_reason: null,
        }),
      },
    );

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("octocat/commitfolio")).toBeInTheDocument();
    });

    await userEvent.click(screen.getByRole("button", { name: "Select octocat/commitfolio" }));
    await userEvent.click(screen.getByRole("button", { name: "Create analysis job" }));

    await waitFor(() => {
      expect(screen.getByText("job_123")).toBeInTheDocument();
    });
    expect(screen.getByText("queued · 0%")).toBeInTheDocument();
  });

  it("runs analysis and shows evidence counts", async () => {
    mockFetchSequence(
      {
        status: 200,
        ok: true,
        json: async () => ({
          id: "github:123",
          github_login: "octocat",
          connected: true,
          name: "The Octocat",
          avatar_url: null,
        }),
      },
      {
        status: 200,
        ok: true,
        json: async () => ({
          items: [
            {
              id: 456,
              full_name: "octocat/commitfolio",
              private: true,
              owner_type: "Organization",
              default_branch: "main",
              permissions: { admin: false, push: true, pull: true },
              html_url: "https://github.com/octocat/commitfolio",
              description: "Portfolio generator",
              updated_at: "2026-04-15T00:00:00Z",
            },
          ],
          next_cursor: null,
        }),
      },
      {
        status: 201,
        ok: true,
        json: async () => ({
          job_id: "job_123",
          status: "queued",
          repository_full_name: "octocat/commitfolio",
          branch: "main",
          progress: { stage: "queued", percent: 0 },
          result_id: null,
          failure_reason: null,
        }),
      },
      {
        status: 200,
        ok: true,
        json: async () => ({
          job: {
            job_id: "job_123",
            status: "completed",
            repository_full_name: "octocat/commitfolio",
            branch: "main",
            progress: { stage: "completed", percent: 100 },
            result_id: null,
            failure_reason: null,
          },
          evidence: {
            job_id: "job_123",
            total_count: 5,
            counts: {
              commit: 1,
              pull_request: 1,
              issue: 1,
              review: 1,
              changed_file: 1,
            },
            latest_events: [
              {
                sequence: 7,
                event_type: "job_completed",
                stage: "completed",
                percent: 100,
                message: "Analysis evidence ingestion completed.",
                payload_json: {},
                created_at: "2026-04-15T00:00:00Z",
              },
            ],
          },
        }),
      },
    );

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("octocat/commitfolio")).toBeInTheDocument();
    });

    await userEvent.click(screen.getByRole("button", { name: "Select octocat/commitfolio" }));
    await userEvent.click(screen.getByRole("button", { name: "Create analysis job" }));

    await waitFor(() => {
      expect(screen.getByText("job_123")).toBeInTheDocument();
    });

    await userEvent.click(screen.getByRole("button", { name: "Run analysis" }));

    await waitFor(() => {
      expect(screen.getByText("5 item(s) collected")).toBeInTheDocument();
    });
    expect(screen.getByText(/Analysis evidence ingestion completed/i)).toBeInTheDocument();
  });



  it("generates and renders a portfolio result", async () => {
    mockFetchSequence(
      {
        status: 200,
        ok: true,
        json: async () => ({
          id: "github:123",
          github_login: "octocat",
          connected: true,
          name: "The Octocat",
          avatar_url: null,
        }),
      },
      {
        status: 200,
        ok: true,
        json: async () => ({
          items: [
            {
              id: 456,
              full_name: "octocat/commitfolio",
              private: true,
              owner_type: "Organization",
              default_branch: "main",
              permissions: { admin: false, push: true, pull: true },
              html_url: "https://github.com/octocat/commitfolio",
              description: "Portfolio generator",
              updated_at: "2026-04-15T00:00:00Z",
            },
          ],
          next_cursor: null,
        }),
      },
      {
        status: 201,
        ok: true,
        json: async () => ({
          job_id: "job_123",
          status: "queued",
          repository_full_name: "octocat/commitfolio",
          branch: "main",
          progress: { stage: "queued", percent: 0 },
          result_id: null,
          failure_reason: null,
        }),
      },
      {
        status: 200,
        ok: true,
        json: async () => ({
          job: {
            job_id: "job_123",
            status: "completed",
            repository_full_name: "octocat/commitfolio",
            branch: "main",
            progress: { stage: "completed", percent: 100 },
            result_id: "res_123",
            failure_reason: null,
          },
          evidence: {
            job_id: "job_123",
            total_count: 1,
            counts: { commit: 1 },
            latest_events: [],
          },
        }),
      },
      {
        status: 200,
        ok: true,
        json: async () => ({
          result_id: "res_123",
          analysis_job_id: "job_123",
          repository_full_name: "octocat/commitfolio",
          version: 1,
          headline: "octocat/commitfolio portfolio draft",
          project_overview: "Project overview text",
          role_summary: "Role summary text",
          key_contributions: ["Built the API"],
          tech_stack: ["Python", "React"],
          evidence_summary: "commit 1개",
          interview_questions: ["What was the key decision?"],
          evidence_links: [
            {
              section_key: "key_contributions",
              label: "commit: Initial commit",
              url: "https://github.com/octocat/commitfolio/commit/abc123",
              evidence_id: "ev_123",
            },
          ],
          created_at: "2026-04-15T00:00:00Z",
          updated_at: "2026-04-15T00:00:00Z",
        }),
      },
      {
        status: 200,
        ok: true,
        json: async () => ({
          items: [
            {
              result_id: "res_123",
              analysis_job_id: "job_123",
              repository_full_name: "octocat/commitfolio",
              headline: "octocat/commitfolio portfolio draft",
              version: 1,
              created_at: "2026-04-15T00:00:00Z",
              updated_at: "2026-04-15T00:00:00Z",
            },
          ],
        }),
      },
      {
        status: 200,
        ok: true,
        json: async () => ({
          result_id: "res_123",
          analysis_job_id: "job_123",
          repository_full_name: "octocat/commitfolio",
          version: 1,
          headline: "Updated portfolio headline",
          project_overview: "Project overview text",
          role_summary: "Role summary text",
          key_contributions: ["Built the API"],
          tech_stack: ["Python", "React"],
          evidence_summary: "commit 1개",
          interview_questions: ["What was the key decision?"],
          evidence_links: [
            {
              section_key: "key_contributions",
              label: "commit: Initial commit",
              url: "https://github.com/octocat/commitfolio/commit/abc123",
              evidence_id: "ev_123",
            },
          ],
          created_at: "2026-04-15T00:00:00Z",
          updated_at: "2026-04-15T00:01:00Z",
        }),
      },
      {
        status: 200,
        ok: true,
        json: async () => ({
          items: [
            {
              result_id: "res_123",
              analysis_job_id: "job_123",
              repository_full_name: "octocat/commitfolio",
              headline: "Updated portfolio headline",
              version: 1,
              created_at: "2026-04-15T00:00:00Z",
              updated_at: "2026-04-15T00:01:00Z",
            },
          ],
        }),
      },
      {
        status: 200,
        ok: true,
        json: async () => ({
          result_id: "res_456",
          analysis_job_id: "job_123",
          repository_full_name: "octocat/commitfolio",
          version: 2,
          headline: "Regenerated portfolio headline",
          project_overview: "Project overview text",
          role_summary: "Role summary text",
          key_contributions: ["Built the API"],
          tech_stack: ["Python", "React"],
          evidence_summary: "commit 1개",
          interview_questions: ["What was the key decision?"],
          evidence_links: [],
          created_at: "2026-04-15T00:02:00Z",
          updated_at: "2026-04-15T00:02:00Z",
        }),
      },
      {
        status: 200,
        ok: true,
        json: async () => ({
          items: [
            {
              result_id: "res_456",
              analysis_job_id: "job_123",
              repository_full_name: "octocat/commitfolio",
              headline: "Regenerated portfolio headline",
              version: 2,
              created_at: "2026-04-15T00:02:00Z",
              updated_at: "2026-04-15T00:02:00Z",
            },
            {
              result_id: "res_123",
              analysis_job_id: "job_123",
              repository_full_name: "octocat/commitfolio",
              headline: "Updated portfolio headline",
              version: 1,
              created_at: "2026-04-15T00:00:00Z",
              updated_at: "2026-04-15T00:01:00Z",
            },
          ],
        }),
      },
    );

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("octocat/commitfolio")).toBeInTheDocument();
    });

    await userEvent.click(screen.getByRole("button", { name: "Select octocat/commitfolio" }));
    await userEvent.click(screen.getByRole("button", { name: "Create analysis job" }));

    await waitFor(() => {
      expect(screen.getByText("job_123")).toBeInTheDocument();
    });

    await userEvent.click(screen.getByRole("button", { name: "Run analysis" }));

    await waitFor(() => {
      expect(screen.getByText("1 item(s) collected")).toBeInTheDocument();
    });

    await userEvent.click(screen.getByRole("button", { name: "Generate portfolio result" }));

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "octocat/commitfolio portfolio draft" })).toBeInTheDocument();
    });
    expect(screen.getAllByText("Built the API").length).toBeGreaterThan(0);
    expect(screen.getByRole("link", { name: "commit: Initial commit" })).toHaveAttribute(
      "href",
      "https://github.com/octocat/commitfolio/commit/abc123",
    );

    await userEvent.clear(screen.getByLabelText("Headline"));
    await userEvent.type(screen.getByLabelText("Headline"), "Updated portfolio headline");
    await userEvent.click(screen.getByRole("button", { name: "Save result edits" }));

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Updated portfolio headline" })).toBeInTheDocument();
    });

    await userEvent.click(screen.getByRole("button", { name: "Regenerate result" }));

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Regenerated portfolio headline" })).toBeInTheDocument();
    });
    expect(screen.getByText(/version 2/i)).toBeInTheDocument();
  });

  it("subscribes to analysis progress with EventSource and stores the last sequence", async () => {
    vi.stubGlobal("EventSource", FakeEventSource);

    mockFetchSequence(
      {
        status: 200,
        ok: true,
        json: async () => ({
          id: "github:123",
          github_login: "octocat",
          connected: true,
          name: "The Octocat",
          avatar_url: null,
        }),
      },
      {
        status: 200,
        ok: true,
        json: async () => ({
          items: [
            {
              id: 456,
              full_name: "octocat/commitfolio",
              private: true,
              owner_type: "Organization",
              default_branch: "main",
              permissions: { admin: false, push: true, pull: true },
              html_url: "https://github.com/octocat/commitfolio",
              description: "Portfolio generator",
              updated_at: "2026-04-15T00:00:00Z",
            },
          ],
          next_cursor: null,
        }),
      },
      {
        status: 201,
        ok: true,
        json: async () => ({
          job_id: "job_123",
          status: "queued",
          repository_full_name: "octocat/commitfolio",
          branch: "main",
          progress: { stage: "queued", percent: 0 },
          result_id: null,
          failure_reason: null,
        }),
      },
      {
        status: 200,
        ok: true,
        json: async () => ({
          job: {
            job_id: "job_123",
            status: "completed",
            repository_full_name: "octocat/commitfolio",
            branch: "main",
            progress: { stage: "completed", percent: 100 },
            result_id: null,
            failure_reason: null,
          },
          evidence: {
            job_id: "job_123",
            total_count: 1,
            counts: { commit: 1 },
            latest_events: [],
          },
        }),
      },
    );

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("octocat/commitfolio")).toBeInTheDocument();
    });

    await userEvent.click(screen.getByRole("button", { name: "Select octocat/commitfolio" }));
    await userEvent.click(screen.getByRole("button", { name: "Create analysis job" }));

    await waitFor(() => {
      expect(screen.getByText("job_123")).toBeInTheDocument();
    });

    sessionStorage.setItem("analysis-job:job_123:last-sequence", "7");
    await userEvent.click(screen.getByRole("button", { name: "Run analysis" }));

    const source = FakeEventSource.instances[0];
    expect(source.url).not.toContain("after=7");
    expect(source.withCredentials).toBe(true);

    act(() => {
      source.onopen?.(new Event("open"));
      source.emit("heartbeat", {
        job_id: "job_123",
        after: 0,
      });
    });

    await waitFor(() => {
      expect(screen.getByText("Progress stream: streaming")).toBeInTheDocument();
    });
    expect(source.close).not.toHaveBeenCalled();

    act(() => {
      source.emit("job_completed", {
        job_id: "job_123",
        sequence: 7,
        event_type: "job_completed",
        stage: "completed",
        percent: 100,
        message: "Analysis evidence ingestion completed.",
        payload_json: {},
        created_at: "2026-04-15T00:00:00Z",
      });
    });

    await waitFor(() => {
      expect(screen.getByText("Progress stream: closed")).toBeInTheDocument();
    });
    expect(sessionStorage.getItem("analysis-job:job_123:last-sequence")).toBe("7");

    act(() => {
      source.emit("job_completed", {
        job_id: "job_123",
        sequence: 7,
        event_type: "job_completed",
        stage: "completed",
        percent: 100,
        message: "Analysis evidence ingestion completed.",
        payload_json: {},
        created_at: "2026-04-15T00:00:00Z",
      });
    });

    expect(screen.getAllByText(/Analysis evidence ingestion completed/i)).toHaveLength(1);
  });

  it("shows repository loading errors", async () => {
    mockFetchSequence(
      {
        status: 200,
        ok: true,
        json: async () => ({
          id: "github:123",
          github_login: "octocat",
          connected: true,
          name: "The Octocat",
          avatar_url: null,
        }),
      },
      {
        status: 502,
        ok: false,
        json: async () => ({
          error: {
            code: "repository_lookup_failed",
            message: "GitHub repository lookup failed.",
          },
        }),
      },
    );

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("GitHub repository lookup failed.")).toBeInTheDocument();
    });
  });
});
