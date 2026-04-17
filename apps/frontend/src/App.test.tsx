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
      expect(screen.getByText("GitHub로 계속하기")).toBeInTheDocument();
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
      expect(screen.getByRole("button", { name: "로그아웃" })).toBeInTheDocument();
    });

    await userEvent.click(screen.getByRole("button", { name: "로그아웃" }));

    await waitFor(() => {
      expect(screen.getByText("GitHub로 계속하기")).toBeInTheDocument();
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

    await userEvent.click(screen.getByRole("button", { name: "octocat/commitfolio 선택" }));

    expect(
      screen.getByText(/저장소로 분석 작업을 만들 수 있습니다/i),
    ).toBeInTheDocument();
  });


  it("loads the next repository page", async () => {
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
          next_cursor: "2",
        }),
      },
      {
        status: 200,
        ok: true,
        json: async () => ({
          items: [
            {
              id: 789,
              full_name: "SERVICE-MOHAENG/Mohaeng-BE",
              private: true,
              owner_type: "Organization",
              default_branch: "develop",
              permissions: { admin: false, push: true, pull: true },
              html_url: "https://github.com/SERVICE-MOHAENG/Mohaeng-BE",
              description: "Mohaeng backend",
              updated_at: "2026-04-14T00:00:00Z",
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

    await userEvent.click(screen.getByRole("button", { name: "저장소 더 불러오기" }));

    await waitFor(() => {
      expect(screen.getAllByText("SERVICE-MOHAENG/Mohaeng-BE").length).toBeGreaterThan(0);
    });
    expect(screen.queryByRole("button", { name: "저장소 더 불러오기" })).not.toBeInTheDocument();
  });


  it("looks up an organization repository by full name", async () => {
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
      {
        status: 200,
        ok: true,
        json: async () => ({
          id: 789,
          full_name: "SERVICE-MOHAENG/Mohaeng-BE",
          private: true,
          owner_type: "Organization",
          default_branch: "develop",
          permissions: { admin: false, push: true, pull: true },
          html_url: "https://github.com/SERVICE-MOHAENG/Mohaeng-BE",
          description: "Mohaeng backend",
          updated_at: "2026-04-17T00:00:00Z",
        }),
      },
    );

    render(<App />);

    await waitFor(() => {
      expect(screen.getByLabelText("저장소 직접 검색")).toBeInTheDocument();
    });

    await userEvent.type(screen.getByLabelText("저장소 직접 검색"), "SERVICE-MOHAENG/Mohaeng-BE");
    await userEvent.click(screen.getByRole("button", { name: "저장소 직접 찾기" }));

    await waitFor(() => {
      expect(screen.getAllByText("SERVICE-MOHAENG/Mohaeng-BE").length).toBeGreaterThan(0);
    });
    expect(screen.getByText("SERVICE-MOHAENG/Mohaeng-BE 저장소를 찾고 선택했습니다.")).toBeInTheDocument();
    expect(screen.getByText("직접 찾음")).toBeInTheDocument();
    expect(screen.getByText(/저장소로 분석 작업을 만들 수 있습니다/i)).toBeInTheDocument();
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

    await userEvent.click(screen.getByRole("button", { name: "octocat/commitfolio 선택" }));
    await userEvent.click(screen.getByRole("button", { name: "분석 작업 만들기" }));

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

    await userEvent.click(screen.getByRole("button", { name: "octocat/commitfolio 선택" }));
    await userEvent.click(screen.getByRole("button", { name: "분석 작업 만들기" }));

    await waitFor(() => {
      expect(screen.getByText("job_123")).toBeInTheDocument();
    });

    await userEvent.click(screen.getByRole("button", { name: "분석 실행" }));

    await waitFor(() => {
      expect(screen.getByText("5개 수집됨")).toBeInTheDocument();
    });
    expect(screen.getByText(/Analysis evidence ingestion completed/i)).toBeInTheDocument();
  });



  it("generates, renders, and exports a portfolio result", async () => {
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
          enhancement_status: "enhanced",
          enhancement_model: "gpt-test",
          enhancement_message: "OpenAI 후처리 적용",
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

    await userEvent.click(screen.getByRole("button", { name: "octocat/commitfolio 선택" }));
    await userEvent.click(screen.getByRole("button", { name: "분석 작업 만들기" }));

    await waitFor(() => {
      expect(screen.getByText("job_123")).toBeInTheDocument();
    });

    await userEvent.click(screen.getByRole("button", { name: "분석 실행" }));

    await waitFor(() => {
      expect(screen.getByText("1개 수집됨")).toBeInTheDocument();
    });

    await userEvent.click(screen.getByRole("button", { name: "포트폴리오 결과 생성" }));

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "octocat/commitfolio portfolio draft" })).toBeInTheDocument();
    });
    expect(screen.getAllByText("Built the API").length).toBeGreaterThan(0);
    expect(screen.getByText("OpenAI 후처리 적용")).toBeInTheDocument();
    expect(screen.getByText(/모델: gpt-test/i)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "commit: Initial commit" })).toHaveAttribute(
      "href",
      "https://github.com/octocat/commitfolio/commit/abc123",
    );
    expect(screen.getByText(/Save as PDF/i)).toBeInTheDocument();

    const printSpy = vi.spyOn(window, "print").mockImplementation(() => undefined);
    await userEvent.click(screen.getByRole("button", { name: "PDF로 저장/출력" }));
    expect(printSpy).toHaveBeenCalledTimes(1);
    printSpy.mockRestore();

    await userEvent.clear(screen.getByLabelText("한 줄 소개"));
    await userEvent.type(screen.getByLabelText("한 줄 소개"), "Updated portfolio headline");
    await userEvent.click(screen.getByRole("button", { name: "수정 내용 저장" }));

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Updated portfolio headline" })).toBeInTheDocument();
    });

    await userEvent.click(screen.getByRole("button", { name: "결과 다시 생성" }));

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

    await userEvent.click(screen.getByRole("button", { name: "octocat/commitfolio 선택" }));
    await userEvent.click(screen.getByRole("button", { name: "분석 작업 만들기" }));

    await waitFor(() => {
      expect(screen.getByText("job_123")).toBeInTheDocument();
    });

    sessionStorage.setItem("analysis-job:job_123:last-sequence", "7");
    await userEvent.click(screen.getByRole("button", { name: "분석 실행" }));

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
      expect(screen.getByText("진행 스트림: 수신 중")).toBeInTheDocument();
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
      expect(screen.getByText("진행 스트림: 종료됨")).toBeInTheDocument();
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
            message: "저장소 목록을 가져오지 못했습니다. 권한 범위와 GitHub 상태를 확인해 주세요.",
          },
        }),
      },
    );

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("저장소 목록을 가져오지 못했습니다. 권한 범위와 GitHub 상태를 확인해 주세요.")).toBeInTheDocument();
    });
  });
});
