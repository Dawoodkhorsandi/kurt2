from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Request
from starlette.responses import RedirectResponse

from src.core.infrastructures.dependency_injection.app_container import AppContainer
from src.core.shorten.schemas.shorten import (
    ShortenRequest,
    ShortenResponse,
    StatsResponse,
)
from src.core.shorten.services.url_shorten_service import UrlShortenService
from src.core.shorten.services.url_visits_service import UrlVisitsService

router = APIRouter()


@router.post("/shorten", response_model=ShortenResponse)
@inject
async def shorten_url(
    request: ShortenRequest,
    url_shorten_service: UrlShortenService = Depends(
        Provide[AppContainer.url_shorten_service]
    ),
):
    return await url_shorten_service.create_short_url(
        original_url=str(request.url),
        custom_code=request.custom_code,
    )


@router.get("/{short_code}")
@inject
async def redirect_to_long_url(
    short_code: str,
    request: Request,
    url_visits_service: UrlVisitsService = Depends(
        Provide[AppContainer.url_visits_service]
    ),
):
    long_url = await url_visits_service.get_original_url(
        short_code=short_code,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
    )
    return RedirectResponse(url=long_url.original_url)


@router.get("/stats/{short_code}", response_model=StatsResponse)
@inject
async def get_url_stats(
    short_code: str,
    url_visits_service: UrlVisitsService = Depends(
        Provide[AppContainer.url_visits_service]
    ),
):
    visits_count = await url_visits_service.get_url_stats(short_code)
    return {"visits": visits_count}
