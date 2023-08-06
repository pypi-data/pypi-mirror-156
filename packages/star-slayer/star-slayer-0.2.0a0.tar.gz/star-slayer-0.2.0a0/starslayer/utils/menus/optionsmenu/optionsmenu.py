"""
Options Menu Module.
"""

from typing import TYPE_CHECKING

from ....auxiliar import Singleton
from ....checks import left_click, on_press
from ....consts import HEIGHT, SFX_AUDIO_ON, WIDTH
from ....gamelib import say as lib_say
from ...menu import ButtonKwargs, Menu, MenuDict
from ...shapes import FloatTuple4

if TYPE_CHECKING:
    from ....scene import Scene
    from ....state import Game
    from ...button import Button


__all__ = ["OptionsMenu"] # We DON'T want the local variable 'optionsmenu' to be exported


class OptionsMenu(Menu, metaclass=Singleton):
    """
    The Options Menu of the game.
    """

    def __init__(self,
                 area_corners: FloatTuple4=(
                    int(WIDTH / 3.75),
                    int(HEIGHT / 2),
                    int(WIDTH / 1.363636),
                    int(HEIGHT / 1.076923)
                 ),
                 **kwargs: MenuDict) -> None:
        """
        Initializes an instance of 'OptionsMenu'.
        """

        super().__init__(area_corners,
                         max_rows=4,
                         **kwargs)


optionsmenu = OptionsMenu() # instantiated temporarily

@optionsmenu.button(message="Configure Controls")
@left_click()
@on_press()
def configure_controls(game: "Game",
                       _scene: "Scene",
                       _btn: "Button",
                       **_kwargs: ButtonKwargs) -> None:
    """
    Goes to the controls menu.
    """

    game.change_scene("scene-controls")


@optionsmenu.button(message="Edit Color Profiles")
@left_click()
@on_press()
def edit_profiles(game: "Game",
                  _scene: "Scene",
                  _btn: "Button",
                  **_kwargs: ButtonKwargs) -> None:
    """
    Goes to the profiles menu.
    """

    game.change_scene("scene-profiles")


@optionsmenu.button(message="Audio On")
@left_click()
@on_press()
def turn_audio(game: "Game",
               _scene: "Scene",
               btn: "Button",
               **_kwargs: ButtonKwargs) -> None:
    """
    Alternates between turning the audio on and off.
    """

    game.has_audio = not game.has_audio
    btn.msg = f"Audio {'On' if game.has_audio else 'Off'}"
    game.play_sound(SFX_AUDIO_ON)


@optionsmenu.button(message="Clear Scores")
@left_click()
@on_press()
def clear_all_scores(game: "Game",
                     _scene: "Scene",
                     _btn: "Button",
                     **_kwargs: ButtonKwargs) -> None:
    """
    Empties the highscores.
    """

    game.clear_scoreboard()
    lib_say("All scores have been cleared!")
