import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import App from "./App";

const originalFetch = global.fetch;

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
