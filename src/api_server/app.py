from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api_server.routes import shorten
from src.core.infrastructures.logging import setup_logging
from src.core.infrastructures.dependency_injection.app_container import AppContainer


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    app.container.wire(
        modules=[
            "src.api_server.routes.shorten",
        ]
    )
    yield
    app.container.unwire()


def create_app() -> FastAPI:
    container = AppContainer()
    app = FastAPI(
        title="Yet Another URL Shortener",
        description="A robust service for shorten your urls.",
        version="1.0.1",
        lifespan=lifespan,
    )
    app.container = container
    app.include_router(shorten.router)

    return app


app = create_app()
