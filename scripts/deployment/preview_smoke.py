#!/usr/bin/env python3
"""Smoke-check Commitfolio preview deployment endpoints.

This script intentionally uses only Python stdlib so it can run from a clean
checkout before backend/frontend dependencies are installed.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from html.parser import HTMLParser
import json
import sys
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urljoin, urlparse
from urllib.request import Request, build_opener, HTTPRedirectHandler


class NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[override]
        return None


NO_REDIRECT_OPENER = build_opener(NoRedirectHandler)


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str


class ScriptCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.scripts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "script":
            return
        attr_map = dict(attrs)
        src = attr_map.get("src")
        if src:
            self.scripts.append(src)


def normalize_url(value: str) -> str:
    return value.rstrip("/")


def request(url: str, *, method: str = "GET", headers: dict[str, str] | None = None, no_redirect: bool = False):
    req = Request(url, method=method, headers=headers or {})
    opener = NO_REDIRECT_OPENER if no_redirect else build_opener()
    try:
        return opener.open(req, timeout=12)
    except HTTPError as error:
        return error


def read_text(url: str, *, headers: dict[str, str] | None = None) -> tuple[int, dict[str, str], str]:
    response = request(url, headers=headers)
    body = response.read().decode("utf-8", errors="replace")
    return response.status, dict(response.headers.items()), body


def check_backend_health(backend_url: str) -> CheckResult:
    url = f"{backend_url}/healthz"
    try:
        status, _, body = read_text(url)
        parsed = json.loads(body)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        return CheckResult("backend health", False, f"{url} failed: {exc}")

    if status == 200 and parsed.get("status") == "ok":
        return CheckResult("backend health", True, f"{url} returned 200 {{status: ok}}")
    return CheckResult("backend health", False, f"{url} returned {status}: {body[:200]}")


def check_oauth_start(backend_url: str) -> CheckResult:
    url = f"{backend_url}/api/v1/auth/github/start"
    try:
        response = request(url, no_redirect=True)
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        return CheckResult("oauth start", False, f"{url} failed: {exc}")

    location = response.headers.get("location", "")
    parsed = urlparse(location)
    query = parse_qs(parsed.query)
    redirect_uri = query.get("redirect_uri", [""])[0]

    if response.status != 302:
        return CheckResult("oauth start", False, f"expected 302, got {response.status}")
    if parsed.netloc != "github.com" or not parsed.path.endswith("/login/oauth/authorize"):
        return CheckResult("oauth start", False, f"expected GitHub authorize redirect, got {location}")
    if not query.get("client_id", [""])[0]:
        return CheckResult("oauth start", False, "GitHub authorize redirect is missing client_id")
    expected_callback_prefix = f"{backend_url}/api/v1/auth/github/callback"
    if redirect_uri != expected_callback_prefix:
        return CheckResult(
            "oauth start",
            False,
            f"redirect_uri mismatch: expected {expected_callback_prefix}, got {redirect_uri}",
        )
    return CheckResult("oauth start", True, f"302 to GitHub with redirect_uri={redirect_uri}")


def check_cors(backend_url: str, frontend_url: str) -> CheckResult:
    url = f"{backend_url}/api/v1/me"
    headers = {
        "Origin": frontend_url,
        "Access-Control-Request-Method": "GET",
    }
    try:
        response = request(url, method="OPTIONS", headers=headers)
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        return CheckResult("cors preflight", False, f"{url} failed: {exc}")

    allow_origin = response.headers.get("access-control-allow-origin")
    allow_credentials = response.headers.get("access-control-allow-credentials")
    if response.status in {200, 204} and allow_origin == frontend_url and allow_credentials == "true":
        return CheckResult("cors preflight", True, f"allow-origin={allow_origin}, credentials={allow_credentials}")
    return CheckResult(
        "cors preflight",
        False,
        f"status={response.status}, allow-origin={allow_origin}, credentials={allow_credentials}",
    )


def collect_frontend_assets(frontend_url: str, html: str) -> list[str]:
    parser = ScriptCollector()
    parser.feed(html)
    return [urljoin(f"{frontend_url}/", src) for src in parser.scripts]


def check_frontend(frontend_url: str) -> tuple[CheckResult, str, list[str]]:
    try:
        status, _, body = read_text(frontend_url)
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        return CheckResult("frontend", False, f"{frontend_url} failed: {exc}"), "", []

    if status != 200:
        return CheckResult("frontend", False, f"expected 200, got {status}"), body, []
    if "root" not in body and "Commitfolio" not in body:
        return CheckResult("frontend", False, "HTML did not look like the Commitfolio app shell"), body, []
    return CheckResult("frontend", True, f"{frontend_url} returned app HTML"), body, collect_frontend_assets(frontend_url, body)


def check_frontend_api_base(
    frontend_url: str,
    frontend_html: str,
    script_urls: Iterable[str],
    expected_api_base: str,
) -> CheckResult:
    haystacks = [(frontend_url, frontend_html)]
    for script_url in script_urls:
        # Vite dev server references /src/main.tsx instead of bundled JS; skip TSX source here.
        if script_url.endswith(".tsx") or "/src/" in script_url:
            continue
        try:
            _, _, body = read_text(script_url)
            haystacks.append((script_url, body))
        except (HTTPError, URLError, TimeoutError, OSError):
            continue

    combined = "\n".join(body for _, body in haystacks)
    if expected_api_base in combined:
        if "http://localhost:8000" in combined and expected_api_base != "http://localhost:8000":
            return CheckResult(
                "frontend api base",
                False,
                "expected API base was found, but localhost backend reference is still present in frontend bundle",
            )
        return CheckResult("frontend api base", True, f"frontend bundle references {expected_api_base}")

    checked = ", ".join(name for name, _ in haystacks) or "no bundled scripts"
    return CheckResult(
        "frontend api base",
        False,
        f"could not find {expected_api_base} in fetched frontend assets ({checked})",
    )


def print_result(result: CheckResult) -> None:
    icon = "PASS" if result.ok else "FAIL"
    print(f"[{icon}] {result.name}: {result.detail}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke-check Commitfolio preview deployment URLs.")
    parser.add_argument("--backend-url", required=True, help="Backend base URL, e.g. https://app.onrender.com")
    parser.add_argument("--frontend-url", help="Frontend base URL, e.g. https://app.vercel.app")
    parser.add_argument(
        "--expected-frontend-api-base",
        help="Expected VITE_API_BASE_URL embedded in the frontend production bundle.",
    )
    args = parser.parse_args()

    backend_url = normalize_url(args.backend_url)
    frontend_url = normalize_url(args.frontend_url) if args.frontend_url else None
    expected_api_base = normalize_url(args.expected_frontend_api_base) if args.expected_frontend_api_base else None

    results: list[CheckResult] = [check_backend_health(backend_url), check_oauth_start(backend_url)]

    frontend_html = ""
    script_urls: list[str] = []
    if frontend_url:
        frontend_result, frontend_html, script_urls = check_frontend(frontend_url)
        results.append(frontend_result)
        results.append(check_cors(backend_url, frontend_url))

    if frontend_url and expected_api_base:
        results.append(check_frontend_api_base(frontend_url, frontend_html, script_urls, expected_api_base))

    for result in results:
        print_result(result)

    failed = [result for result in results if not result.ok]
    if failed:
        print(f"\n{len(failed)} check(s) failed.", file=sys.stderr)
        return 1
    print("\nAll preview smoke checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
