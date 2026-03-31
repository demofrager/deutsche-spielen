from fastapi import FastAPI

from app.api.routes_wortschatzblitz import router as wortschatzblitz_router
from app.api.routes_satzbauwuerfeln import router as satzbauwuerfeln_router


# Extension point: add new game routers here.
GAME_ROUTERS = (
    satzbauwuerfeln_router,
    wortschatzblitz_router,
)


def include_game_routers(app: FastAPI) -> None:
    for router in GAME_ROUTERS:
        app.include_router(router)
