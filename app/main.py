from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes_games import router as games_router
from app.api.routes_menu import router as menu_router
from app.api.routes_satzbauwuerfeln import router as satzbauwuerfeln_router

BASE_DIR = Path(__file__).resolve().parent


def create_app() -> FastAPI:
    app = FastAPI(title="Deutsche Spielen", version="0.1.0")

    app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

    app.include_router(menu_router)
    app.include_router(games_router)
    app.include_router(satzbauwuerfeln_router)

    return app


app = create_app()
