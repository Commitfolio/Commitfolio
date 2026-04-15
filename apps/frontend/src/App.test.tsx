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
});
