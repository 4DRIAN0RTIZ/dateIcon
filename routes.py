import hashlib

from fastapi import APIRouter, Query, HTTPException, Request, Response
from fastapi.responses import StreamingResponse
from typing import Optional
from slowapi import Limiter
from slowapi.util import get_remote_address

from config import Theme, Language, THEMES, LANGUAGES_INFO, SIZES_ALLOWED, settings

from service import DateIconService

router = APIRouter()
icon_service = DateIconService()
limiter = Limiter(key_func=get_remote_address)

CACHE_CONTROL_VALUE = "public, max-age=86400"


def _icon_etag(
    date: str,
    theme: str,
    lang: str,
    size: int,
    bar_color: Optional[str],
    bg_color: Optional[str],
    text_color: Optional[str],
) -> str:
    """Build a stable strong ETag from the effective icon request parameters."""
    parts = [date, theme, lang, str(size)]
    if theme == "custom":
        parts.extend([bar_color or "", bg_color or "", text_color or ""])
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:32]
    return f'"{digest}"'


@router.get("/")
def root():
    """API root endpoint with usage information."""
    return {
        "name": "Date Icon API",
        "version": "1.0.0",
        "endpoints": {
            "/icon/{date}": "Generate date icon (date format: DD_MM)",
            "/themes": "List available themes",
            "/languages": "List available languages",
            "/sizes": "List allowed sizes",
            "/health": "Liveness / health check",
        },
        "example": "/icon/25_12?theme=default&lang=es&size=128",
    }


@router.get("/icon/{date}")
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
def generate_icon(
    request: Request,
    date: str,
    theme: Theme = Query(Theme.DEFAULT, description="Color theme"),
    lang: Language = Query(Language.ES, description="Language for month names"),
    size: int = Query(64, description="Icon size in pixels"),
    bar_color: Optional[str] = Query(
        None, description="Custom bar color (hex, only with custom theme)"
    ),
    bg_color: Optional[str] = Query(
        None, description="Custom background color (hex, only with custom theme)"
    ),
    text_color: Optional[str] = Query(
        None, description="Custom text color (hex, only with custom theme)"
    ),
):
    """Generate a date icon with the specified date, theme and language."""
    try:
        img_io = icon_service.generate(
            date_str=date,
            size=size,
            theme=theme.value,
            lang=lang.value,
            custom_bar_color=bar_color,
            custom_bg_color=bg_color,
            custom_text_color=text_color,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    etag = _icon_etag(
        date, theme.value, lang.value, size, bar_color, bg_color, text_color
    )
    headers = {"Cache-Control": CACHE_CONTROL_VALUE, "ETag": etag}

    if request.headers.get("if-none-match") == etag:
        return Response(status_code=304, headers=headers)

    return StreamingResponse(img_io, media_type="image/png", headers=headers)


@router.get("/themes")
def list_themes():
    """List all available themes with their color configurations."""
    return {"themes": THEMES}


@router.get("/languages")
def list_languages():
    """List all available languages."""
    return {"languages": LANGUAGES_INFO}


@router.get("/sizes")
def list_sizes():
    """List all allowed icon sizes."""
    return {"sizes": SIZES_ALLOWED}


@router.get("/health")
def health():
    """Liveness probe for uptime checks and Render health checks."""
    return {"status": "ok"}
