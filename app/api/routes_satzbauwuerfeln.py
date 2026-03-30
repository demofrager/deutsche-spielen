from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, field_validator

from app.domain.sentence_validation import validate_sentence
from app.services.satzbauwuerfeln_service import perform_roll

router = APIRouter(tags=["satzbauwuerfeln"])
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


# --- Response models ---

class DieOut(BaseModel):
    value: int
    label: str
    question: str
    suggestion: str


class SentenceTypeOut(BaseModel):
    letter: str
    label: str


class RollOut(BaseModel):
    dice: list[DieOut]
    sentence_type: SentenceTypeOut


class ValidateIn(BaseModel):
    sentence: str
    suggestions: list[str]
    sentence_type_letter: str

    @field_validator("sentence_type_letter")
    @classmethod
    def must_be_valid_letter(cls, v: str) -> str:
        if v not in "ABCDEF":
            raise ValueError("sentence_type_letter must be A-F")
        return v


class ValidateOut(BaseModel):
    is_valid: bool
    checks_passed: list[str]
    checks_failed: list[str]
    message: str


# --- Routes ---

@router.get("/games/satzbauwuerfeln", response_class=HTMLResponse)
def satzbauwuerfeln(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="satzbauwuerfeln.html",
        context={"page_title": "Satzbauwuerfeln"},
    )


@router.post("/api/games/satzbauwuerfeln/roll", response_model=RollOut)
def roll() -> RollOut:
    result = perform_roll()
    return RollOut(
        dice=[
            DieOut(
                value=d.value,
                label=d.label,
                question=d.question,
                suggestion=d.suggestion,
            )
            for d in result.dice
        ],
        sentence_type=SentenceTypeOut(
            letter=result.sentence_type.letter,
            label=result.sentence_type.label,
        ),
    )


@router.post("/api/games/satzbauwuerfeln/validate", response_model=ValidateOut)
def validate(body: ValidateIn) -> ValidateOut:
    result = validate_sentence(
        sentence=body.sentence,
        suggestions=body.suggestions,
        sentence_type_letter=body.sentence_type_letter,
    )
    return ValidateOut(
        is_valid=result.is_valid,
        checks_passed=result.checks_passed,
        checks_failed=result.checks_failed,
        message=result.message,
    )
