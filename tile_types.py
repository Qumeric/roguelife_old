from typing import Any, TypeAlias

from numpy.typing import NDArray
import numpy as np

# Tile graphics structured type compatible with Console.tiles_rgb.
graphic_dt = np.dtype(
    [
        ("ch", np.int32),  # Unicode codepoint.
        ("fg", "3B"),  # 3 unsigned bytes, for RGB colors.
        ("bg", "3B"),
    ]
)

Tile: TypeAlias = NDArray[Any]

# Tile struct used for statically defined tile data.
tile_dt = np.dtype(
    [
        ("walkable", bool),  # True if this tile can be walked over.
        ("transparent", bool),  # True if this tile doesn't block FOV.
        ("dark", graphic_dt),  # Graphics for when this tile is not in FOV.
        ("light", graphic_dt),  # Graphics for when the tile is in FOV.
        ("name", str, 20),
    ]
)


def new_tile(
    *,  # Enforce the use of keywords, so that parameter order doesn't matter.
    walkable: int,
    transparent: int,
    dark: tuple[int, tuple[int, int, int], tuple[int, int, int]],
    light: tuple[int, tuple[int, int, int], tuple[int, int, int]],
    name: str,
) -> NDArray[Any]:
    """Helper function for defining individual tile types"""
    return np.array((walkable, transparent, dark, light, name), dtype=tile_dt)


def is_walkable(tile: Tile) -> bool:
    return tile[0]


def is_transparent(tile: Tile) -> bool:
    return tile[1]


def get_name(tile: Tile) -> str:
    return tile[4]


# SHROUD represents unexplored, unseen tiles
SHROUD = np.array((ord(" "), (255, 255, 255), (0, 0, 0)), dtype=graphic_dt)

floor = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord(" "), (255, 255, 255), (50, 50, 150)),
    light=(ord(" "), (255, 255, 255), (200, 180, 50)),
    name="floor",
)

wall = new_tile(
    walkable=False,
    transparent=False,
    dark=(ord(" "), (255, 255, 255), (0, 0, 100)),
    light=(ord(" "), (255, 255, 255), (130, 110, 50)),
    name="wall",
)

water = new_tile(
    walkable=False,
    transparent=True,
    dark=(ord(" "), (255, 255, 255), (0, 0, 100)),
    light=(ord(" "), (255, 255, 255), (0, 0, 255)),
    name="water",
)

sand = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord(" "), (255, 255, 255), (100, 100, 0)),
    light=(ord(" "), (255, 255, 255), (255, 255, 0)),
    name="sand",
)

grass = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord(" "), (255, 255, 255), (0, 100, 0)),
    light=(ord(" "), (255, 255, 255), (0, 255, 0)),
    name="grass",
)

forrest = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord(" "), (255, 255, 255), (0, 70, 0)),
    light=(ord(" "), (255, 255, 255), (0, 190, 0)),
    name="forrest",
)

mountain = new_tile(
    walkable=False,
    transparent=False,
    dark=(ord(" "), (255, 255, 255), (100, 100, 100)),
    light=(ord(" "), (255, 255, 255), (255, 255, 255)),
    name="mountain",
)
