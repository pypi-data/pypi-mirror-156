"""
Main Menu Module.
"""

from typing import TYPE_CHECKING

from ....auxiliar import Singleton
from ....checks import left_click, on_press
from ....consts import HEIGHT, WIDTH
from ...menu import ButtonKwargs, Menu, MenuDict
from ...shapes import FloatTuple4

if TYPE_CHECKING:
    from ....scene import Scene
    from ....state import Game
    from ...button import Button


__all__ = ["MainMenu"] # We DON'T want the local variable 'mainmenu' to be exported


class MainMenu(Menu, metaclass=Singleton):
    """
    The Main Menu of the game.
    """

    def __init__(self,
                 area_corners: FloatTuple4=(
                    int(WIDTH / 3.75),
                    int(HEIGHT / 1.75),
                    int(WIDTH / 1.363636),
                    int(HEIGHT / 1.1)
                 ),
                 **kwargs: MenuDict) -> None:
        """
        Initializes an instance of 'MainMenu'.
        """

        super().__init__(area_corners,
                         max_rows=3,
                         special_btn_on_right=False,
                         **kwargs)


mainmenu = MainMenu() # instantiated temporarily

@mainmenu.button(message="Play")
@left_click()
@on_press()
def play_game(game: "Game", _scene: "Scene", _btn: "Button", **_kwargs: ButtonKwargs) -> None:
    """
    Lets the player play the game.
    """

    game.change_scene("scene-characters")


@mainmenu.button(message="Options")
@left_click()
@on_press()
def go_to_options(game: "Game", _scene: "Scene", _btn: "Button", **_kwargs: ButtonKwargs) -> None:
    """
    Goes to the options menu.
    """

    game.change_scene("scene-options")


@mainmenu.button(message="Exit")
@left_click()
@on_press()
def exit_game(game: "Game", _scene: "Scene", _btn: "Button", **_kwargs: ButtonKwargs) -> None:
    """
    Exits the game.
    """

    game.exit = True


@mainmenu.button(message="About")
@left_click()
@on_press()
def about_game(game: "Game", _scene: "Scene", _btn: "Button", **_kwargs: ButtonKwargs) -> None:
    """
    Shows information about the game.
    """

    game.change_scene("scene-about")


@mainmenu.button(message="Highscores")
@left_click()
@on_press()
def show_scores(game: "Game", _scene: "Scene", _btn: "Button", **_kwargs: ButtonKwargs) -> None:
    """
    Shows the scoreboard of the game.
    """

    game.change_scene("scene-scoreboard")
