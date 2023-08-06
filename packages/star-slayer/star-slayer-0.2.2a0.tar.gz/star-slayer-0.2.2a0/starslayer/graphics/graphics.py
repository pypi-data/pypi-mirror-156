"""
Graphics Module. Draws anything that the player
sees on screen.
"""

from sys import version_info
from typing import TYPE_CHECKING, Optional

from .background import draw_background, draw_default_background
from .gameplay import draw_bullets, draw_debug_info
from .gui import draw_exiting_bar, draw_gui
from .sprites import draw_sprite

if TYPE_CHECKING:
    from ..graphics import SceneDrawer
    from ..state import Game


def draw_screen(game: "Game",
                _cursor_x: Optional[int],
                _cursor_y: Optional[int],
                scene_drawer: "SceneDrawer") -> None:
    """
    Draws the entirety of the elements on the screen.
    """

    if version_info < (3, 10, 0): # Inferior to v3.10.0

        draw_default_background()
        return

    draw_background(game)
    draw_bullets(game)

    if game.is_in_game:

        for drop in game.drops:
            draw_sprite(drop.sprite,
                        drop.x1,
                        drop.y1,
                        drop.x2,
                        drop.y2)

        for enem in game.enemies:
            draw_sprite(enem.sprite,
                        enem.x1,
                        enem.y1,
                        enem.x2,
                        enem.y2)

        draw_sprite(game.player.sprite,
                    game.player.x1,
                    game.player.y1,
                    game.player.x2,
                    game.player.y2)

        if game.player.satellite:
            sh_x1, sh_y1, sh_x2, sh_y2 = game.player.satellite.all_coords
            draw_sprite(game.player.satellite.sprite,
                        sh_x1,
                        sh_y1,
                        sh_x2,
                        sh_y2,
                        sprite_type="CIRCLE")

        if game.show_debug_info:
            draw_debug_info(game)

        draw_gui(game)

    scene_drawer.draw_scene()

    if game.exiting:
        draw_exiting_bar(game)
