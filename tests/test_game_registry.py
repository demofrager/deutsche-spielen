from fastapi import FastAPI

from app.api.game_router_registry import GAME_ROUTERS, include_game_routers
from app.domain.game_registry import list_games


def test_list_games_contains_satzbauwuerfeln() -> None:
    games = list_games()
    assert games
    assert games[0].slug == "satzbauwuerfeln"
    assert games[0].path == "/games/satzbauwuerfeln"
    assert all(g.slug != "wortschatzblitz" for g in games)


def test_list_games_include_hidden_contains_stub() -> None:
    games = list_games(include_hidden=True)
    slugs = {g.slug for g in games}
    assert "satzbauwuerfeln" in slugs
    assert "wortschatzblitz" in slugs


def test_include_game_routers_registers_expected_paths() -> None:
    app = FastAPI()
    include_game_routers(app)

    paths = {route.path for route in app.routes}
    assert "/games/satzbauwuerfeln" in paths
    assert "/games/wortschatzblitz" in paths
    assert "/api/games/satzbauwuerfeln/roll" in paths
    assert "/api/games/satzbauwuerfeln/validate" in paths
    assert len(GAME_ROUTERS) >= 1
