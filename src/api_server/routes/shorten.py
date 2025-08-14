from fastapi import APIRouter, Depends, Request
from starlette.responses import RedirectResponse
from dependency_injector.wiring import inject, Provide

from src.core.shorten.services.url_shorten_service import UrlShortenService
from src.core.shorten.services.url_visits_service import UrlVisitsService
from src.core.infrastructures.dependency_injection.appcontainer import AppContainer

router = APIRouter()
container = AppContainer()

@router.post("/shorten")
@inject
def shorten_url(url: str, url_shorten_service: UrlShortenService = Depends(Provide[AppContainer.url_shorten_service])):
    short_code = url_shorten_service.create_short_url(url)
    return {"short_code": short_code}

@router.get("/{short_code}")
@inject
async def redirect_to_long_url(short_code: str, request: Request, url_visits_service: UrlVisitsService = Depends(Provide[AppContainer.url_visits_service])):
    long_url = await url_visits_service.get_original_url(
        short_code=short_code,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
    )
    return RedirectResponse(url=long_url)

@router.get("/stats/{short_code}")
@inject
async def get_url_stats(short_code: str, url_visits_service: UrlVisitsService = Depends(Provide[AppContainer.url_visits_service])):
    visits = await url_visits_service.get_url_stats(short_code)
    return {"visits": visits}
