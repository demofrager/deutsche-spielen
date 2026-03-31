from dataclasses import dataclass


@dataclass(frozen=True)
class GameDefinition:
    slug: str
    title: str
    description: str
    path: str
    visible: bool = True


# Central catalog for game metadata used by pages and navigation.
_GAMES: tuple[GameDefinition, ...] = (
    GameDefinition(
        slug="satzbauwuerfeln",
        title="Satzbauwuerfeln",
        description=(
            "Roll dice for sentence elements and sentence type, then build your own "
            "German sentence."
        ),
        path="/games/satzbauwuerfeln",
    ),
    GameDefinition(
        slug="wortschatzblitz",
        title="Wortschatzblitz (Stub)",
        description="Internal stub for future vocabulary game development.",
        path="/games/wortschatzblitz",
        visible=False,
    ),
)


def list_games(*, include_hidden: bool = False) -> list[GameDefinition]:
    if include_hidden:
        return list(_GAMES)
    return [game for game in _GAMES if game.visible]
