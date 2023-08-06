"""
Common Enemy B Module.
"""

from typing import TYPE_CHECKING, List, Optional

from ...bullets import BulletAccel
from ...consts import ENEMY_COMMON_B_REL_PATH, HEIGHT, WIDTH
from ...drops import MedKit
from ...entity import EntityDict
from ...utils import SpringTimer
from ..enemy import Enemy

if TYPE_CHECKING:
    from ...drops import Drop
    from ...state import BulletsList

class EnemyCommonB(Enemy):
    """
    A common enemy (B version).
    """

    def __init__(self,
                 *,
                 health=3,
                 how_hard=5,
                 speed=3,
                 internal_spring_timer_initial: int=30,
                 initial_direction: int=0, # 0 for "LEFT", 1 for "DOWN" and 2 for "RIGHT"
                 shooting_cooldown=200,
                 **kwargs: EntityDict) -> None:
        """
        Initializes an instance of type 'EnemyCommonB'.
        """

        super().__init__(health=health,
                         how_hard=how_hard,
                         speed=speed,
                         shooting_cooldown=shooting_cooldown,
                         texture_path=ENEMY_COMMON_B_REL_PATH,
                         **kwargs)

        self.internal_spring_timer = SpringTimer(0,
                                                 internal_spring_timer_initial,
                                                 internal_spring_timer_initial)
        self.direction = initial_direction


    def trajectory(self) -> None:
        """
        Defines the movement of a common enemy (B version).
        """

        if self.internal_spring_timer.is_at_floor():
            self.direction += 1

        elif self.internal_spring_timer.is_at_ceiling():
            self.direction -= 1

        elif self.internal_spring_timer.current_time == self.internal_spring_timer.ceil // 2:
            if self.internal_spring_timer.adding:
                self.direction = (self.direction + 1) % 3

            else:
                self.direction = (self.direction + 2) % 3

        self.internal_spring_timer.count()

        self.transfer((-self.speed if self.direction == 0
                                   else (self.speed if self.direction == 2 else 0)),
                      ((self.speed // 2) if self.direction == 1 else 0))


    @property
    def points_worth(self) -> int:
        """
        How many points should this enemy be worth at dying.
        """

        return 46


    @property
    def loot_drops(self) -> List[Optional["Drop"]]:
        """
        Returns the possible drops for this enemy.
        """

        return [None, MedKit]


    @property
    def loot_weights(self) -> Optional[List[float]]:
        """
        Returns the weights of the loot drops,
        and it must be of the same length.
        """

        return [90.0, 10.0]


    def shoot_bullets(self, bullets: "BulletsList") -> None:
        """
        Shoots the bullets specially made for this enemy.
        """

        center_x, center_y = self.center
        aux_y = HEIGHT / 46.6667
        rad_aux = WIDTH // 150

        bullets.append(BulletAccel(cx=center_x,
                                   cy=center_y + aux_y,
                                   radius=rad_aux,
                                   speed=4,
                                   how_hard=2,
                                   upwards=False,
                                   can_spawn_outside=True))
