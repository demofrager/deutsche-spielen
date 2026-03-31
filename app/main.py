from pathlib import Path
import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.game_router_registry import include_game_routers
from app.api.routes_games import router as games_router
from app.api.routes_menu import router as menu_router
from app.services.grammar_service import get_languagetool_url, is_languagetool_available

BASE_DIR = Path(__file__).resolve().parent
LOGGER = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(title="Deutsche Spielen", version="0.1.0")

    app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

    app.include_router(menu_router)
    app.include_router(games_router)
    include_game_routers(app)

    @app.on_event("startup")
    def check_grammar_service() -> None:
        lt_url = get_languagetool_url()
        if not lt_url:
            LOGGER.info("LanguageTool is disabled (LANGUAGETOOL_URL not set).")
            return
        if is_languagetool_available():
            LOGGER.info("LanguageTool is available at %s", lt_url)
            return
        LOGGER.warning(
            "LanguageTool configured at %s but unavailable. Continuing with Phase 1 validation only.",
            lt_url,
        )

    return app


app = create_app()
