from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["games"])
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@router.get("/games", response_class=HTMLResponse)
def games(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="games.html",
        context={"page_title": "Games"},
    )
