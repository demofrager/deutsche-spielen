from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.domain.game_registry import list_games

router = APIRouter(tags=["wortschatzblitz"])
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@router.get("/games/wortschatzblitz", response_class=HTMLResponse)
def wortschatzblitz(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="wortschatzblitz.html",
        context={
            "page_title": "Wortschatzblitz (Stub)",
            "games": list_games(),
        },
    )
