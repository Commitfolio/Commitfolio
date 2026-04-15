from __future__ import annotations

from urllib.parse import urlencode

from fastapi.responses import JSONResponse


def build_frontend_redirect(frontend_app_url: str, **query: str) -> str:
    encoded = urlencode(query)
    return f"{frontend_app_url}/?{encoded}" if encoded else frontend_app_url


def build_error_response(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
            }
        },
    )
