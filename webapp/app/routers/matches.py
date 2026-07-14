from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.auth import get_current_player
from app.services.matches import (
    get_match_or_404,
    get_match_summary,
    get_round_detail,
    list_matches,
    list_matches_for_player,
)
from app.templates import templates

router = APIRouter(prefix="/matches", tags=["matches"])


@router.get("")
def match_list(
    request: Request,
    show_all: bool = Query(False, alias="all"),
    db: Session = Depends(get_db),
):
    current_player = get_current_player(request, db)
    showing_own_matches = current_player is not None and not show_all
    matches = (
        list_matches_for_player(db, current_player.id) if showing_own_matches else list_matches(db)
    )
    return templates.TemplateResponse(
        request,
        "matches/list.html",
        {"matches": matches, "showing_own_matches": showing_own_matches},
    )


@router.get("/{external_id}")
def match_detail(request: Request, external_id: str, db: Session = Depends(get_db)):
    match = get_match_or_404(db, external_id)
    summary = get_match_summary(db, match)
    chart_data = {
        "labels": summary.round_numbers,
        "series": [
            {
                "label": f"{p.display_name} ({p.agent})",
                "data": [p.impact_by_round.get(r) for r in summary.round_numbers],
            }
            for p in summary.players
        ],
    }
    return templates.TemplateResponse(
        request,
        "matches/detail.html",
        {"match": match, "summary": summary, "chart_data": chart_data},
    )


@router.get("/{external_id}/rounds/{round_number}")
def round_detail(request: Request, external_id: str, round_number: int, db: Session = Depends(get_db)):
    match = get_match_or_404(db, external_id)
    detail = get_round_detail(db, match, round_number)
    return templates.TemplateResponse(
        request, "matches/_round_detail.html", {"match": match, "detail": detail}
    )
