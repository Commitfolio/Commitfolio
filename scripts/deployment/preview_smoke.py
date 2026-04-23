#!/usr/bin/env python3
"""Smoke-check Commitfolio preview deployment endpoints.

This script intentionally uses only Python stdlib so it can run from a clean
checkout before backend/frontend dependencies are installed.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
import re
from pathlib import Path
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


def check_me_endpoint_contract(backend_url: str) -> CheckResult:
    url = f"{backend_url}/api/v1/me"
    try:
        status, headers, body = read_text(url)
        parsed = json.loads(body)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        return CheckResult("me endpoint contract", False, f"{url} failed: {exc}")

    error = parsed.get("error", {})
    request_id = headers.get("X-Request-ID") or headers.get("x-request-id")
    if status == 401 and error.get("code") == "unauthenticated" and request_id:
        return CheckResult(
            "me endpoint contract",
            True,
            f"{url} returned 401 unauthenticated with X-Request-ID={request_id}",
        )
    return CheckResult(
        "me endpoint contract",
        False,
        f"expected 401 unauthenticated with X-Request-ID, got status={status}, body={body[:200]}",
    )


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


def _contains_runtime_api_base_reference(content: str, expected_api_base: str) -> bool:
    runtime_patterns = [
        rf'const\s+\w+\s*=\s*["\']{re.escape(expected_api_base)}["\']',
        rf'fetch\(`{re.escape(expected_api_base)}',
        rf'fetch\(["\']{re.escape(expected_api_base)}',
    ]
    return any(re.search(pattern, content) for pattern in runtime_patterns)


def _contains_localhost_runtime_api_base_reference(content: str) -> bool:
    localhost_patterns = [
        r'const\s+\w+\s*=\s*["\']http://localhost:8000["\']',
        r'fetch\(`http://localhost:8000',
        r'fetch\(["\']http://localhost:8000',
    ]
    return any(re.search(pattern, content) for pattern in localhost_patterns)


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
        if _contains_localhost_runtime_api_base_reference(combined) and expected_api_base != "http://localhost:8000":
            return CheckResult(
                "frontend api base",
                False,
                "frontend runtime still assigns localhost backend as the API base",
            )
        if _contains_runtime_api_base_reference(combined, expected_api_base):
            return CheckResult("frontend api base", True, f"frontend bundle references {expected_api_base}")

    checked = ", ".join(name for name, _ in haystacks) or "no bundled scripts"
    return CheckResult(
        "frontend api base",
        False,
        f"could not confirm runtime API base {expected_api_base} in fetched frontend assets ({checked})",
    )


def print_result(result: CheckResult) -> None:
    icon = "PASS" if result.ok else "FAIL"
    print(f"[{icon}] {result.name}: {result.detail}")


def summarize_results(results: list[CheckResult]) -> dict[str, int | bool]:
    failed = sum(1 for result in results if not result.ok)
    return {
        "total": len(results),
        "failed": failed,
        "passed": len(results) - failed,
        "ok": failed == 0,
    }


def validate_mode_requirements(
    mode: str,
    *,
    frontend_url: str | None,
    expected_api_base: str | None,
) -> None:
    if mode in {"preview", "release"} and not frontend_url:
        raise ValueError(f"--mode {mode} requires --frontend-url")
    if mode == "release" and not expected_api_base:
        raise ValueError("--mode release requires --expected-frontend-api-base")


def build_followup_steps(mode: str, results: list[CheckResult]) -> list[str]:
    followups: list[str] = []
    failed_checks = {result.name for result in results if not result.ok}

    mode_hints = {
        "backend": "backend smoke가 통과하면 frontend 연결 후 preview/release smoke로 확장합니다.",
        "preview": "preview smoke 후에는 실제 브라우저에서 GitHub 로그인과 저장소 선택 흐름을 한 번 더 확인합니다.",
        "release": "release smoke 후에는 public/private/org 저장소 샘플 검증 결과와 deploy URL을 PR/작업 문서에 기록합니다.",
    }
    followups.append(mode_hints[mode])

    failure_hints = {
        "backend health": "backend health 실패 시 Render deploy 로그와 DATABASE_URL/PORT 설정을 다시 확인합니다.",
        "me endpoint contract": "me endpoint contract 실패 시 세션 미들웨어, observability, unauthenticated envelope 응답을 점검합니다.",
        "oauth start": "oauth start 실패 시 GITHUB_CLIENT_ID/GITHUB_CALLBACK_URL과 GitHub OAuth callback URL을 맞춥니다.",
        "frontend": "frontend 실패 시 Vercel deploy 상태와 build output을 확인합니다.",
        "cors preflight": "CORS 실패 시 BACKEND_CORS_ORIGIN, SESSION_COOKIE_SAME_SITE, SESSION_COOKIE_SECURE를 점검합니다.",
        "frontend api base": "frontend api base 실패 시 VITE_API_BASE_URL과 배포 후 번들 교체 여부를 확인합니다.",
    }
    for name in (
        "backend health",
        "me endpoint contract",
        "oauth start",
        "frontend",
        "cors preflight",
        "frontend api base",
    ):
        if name in failed_checks:
            followups.append(failure_hints[name])

    if not failed_checks:
        followups.append("실패한 체크가 없으면 operator playbook의 다음 사용자 액션만 진행하면 됩니다.")

    return followups


def write_json_report(
    path: str,
    *,
    mode: str,
    backend_url: str,
    frontend_url: str | None,
    expected_api_base: str | None,
    results: list[CheckResult],
) -> None:
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": mode,
        "backend_url": backend_url,
        "frontend_url": frontend_url,
        "expected_frontend_api_base": expected_api_base,
        "summary": summarize_results(results),
        "results": [
            {
                "name": result.name,
                "ok": result.ok,
                "detail": result.detail,
            }
            for result in results
        ],
        "next_steps": build_followup_steps(mode, results),
    }

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke-check Commitfolio preview deployment URLs.")
    parser.add_argument(
        "--mode",
        choices=("backend", "preview", "release"),
        default="preview",
        help="backend=backend-only, preview=split-domain preview sanity, release=public release evidence",
    )
    parser.add_argument("--backend-url", required=True, help="Backend base URL, e.g. https://app.onrender.com")
    parser.add_argument("--frontend-url", help="Frontend base URL, e.g. https://app.vercel.app")
    parser.add_argument(
        "--expected-frontend-api-base",
        help="Expected VITE_API_BASE_URL embedded in the frontend production bundle.",
    )
    parser.add_argument(
        "--report-json",
        help="Write a structured JSON smoke report to this path.",
    )
    args = parser.parse_args()

    backend_url = normalize_url(args.backend_url)
    frontend_url = normalize_url(args.frontend_url) if args.frontend_url else None
    expected_api_base = normalize_url(args.expected_frontend_api_base) if args.expected_frontend_api_base else None
    try:
        validate_mode_requirements(args.mode, frontend_url=frontend_url, expected_api_base=expected_api_base)
    except ValueError as error:
        parser.error(str(error))

    results: list[CheckResult] = [
        check_backend_health(backend_url),
        check_me_endpoint_contract(backend_url),
        check_oauth_start(backend_url),
    ]

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

    next_steps = build_followup_steps(args.mode, results)
    print("\nNext steps:")
    for step in next_steps:
        print(f"- {step}")

    if args.report_json:
        write_json_report(
            args.report_json,
            mode=args.mode,
            backend_url=backend_url,
            frontend_url=frontend_url,
            expected_api_base=expected_api_base,
            results=results,
        )
        print(f"\nJSON report written to {args.report_json}")

    failed = [result for result in results if not result.ok]
    if failed:
        print(f"\n{len(failed)} check(s) failed for {args.mode} smoke.", file=sys.stderr)
        return 1
    print(f"\nAll {args.mode} smoke checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
