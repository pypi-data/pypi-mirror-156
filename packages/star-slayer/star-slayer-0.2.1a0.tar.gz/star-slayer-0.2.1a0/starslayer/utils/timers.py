"""
Timers Module. Contains simple timers to
handle event timing.
"""

from typing import List, Optional


class Timer:
    """
    Class for a simple timer that counts
    from a certain number to 0.
    """

    def __init__(self,
                 base_time: float,
                 *,
                 dest_time: float=0.0,
                 init_time: Optional[float]=None,
                 message: str='') -> None:
        """
        Initializes an instance of type 'Timer'.
        """

        if base_time < 0:
            raise ValueError("Base Time must be of value above zero.")

        self.base_time: float = base_time
        self.goal_time: float = dest_time
        self.current_time: float = init_time or base_time
        self.msg: str = message


    def __str__(self) -> str:
        """
        Returns a string with class information so it can be printed later.
        """

        return (f"Initial Time: {self.base_time} - Goal Time: {self.goal_time} " +
                f"- Current Time: {self.current_time}" +
                f"{f' - Message: {self.msg}' if self.msg != '' else ''}")


    def deduct(self, how_much: float) -> None:
        """
        Descends the countdown subtracting 'how_much' time from 'self.current_time'.
        """

        self.current_time -= float(how_much)


    def count(self, how_much: float, reset: bool=False) -> None:
        """
        Count the timer to zero.
        if 'reset' is set to 'True', it automatically restarts the timer.
        """

        if not self.time_is_up():
            self.deduct(float(how_much))

        elif reset:
            self.reset()


    def reset(self) -> None:
        """
        Resets the timer to its original value ('self.initial_value').
        """

        self.current_time = self.base_time
        self.msg = ''


    def drop(self) -> None:
        """
        Drops the timer to its goal time.
        """

        self.current_time = self.goal_time


    def time_is_up(self) -> bool:
        """
        Returns 'True' if the current time of the Timer reaches the goal time or further,
        or 'False' otherwise.
        """

        return self.current_time <= self.goal_time


    def change_message(self, new_message: str) -> None:
        """
        Changes the current message to a given new one.
        """

        self.msg = new_message


class SpringTimer:
    """
    Simple timer that oscillates between
    given 'floor' and 'ceiling' values.
    """

    def __init__(self,
                 floor: float,
                 ceiling: float,
                 where_to_start: float,
                 is_it_adding: bool=True) -> None:
        """
        Initializes an instance of type 'SpringTimer'.
        """

        if floor >= ceiling:

            raise ValueError("'floor' parameter must NOT be greater or equal than 'ceiling'")

        if where_to_start < floor or where_to_start > ceiling:

            raise ValueError("'where_to_start' parameter needs to be between " +
                             f"{floor} and {ceiling} inclusive")

        self.floor: float = floor
        self.ceil: float = ceiling
        self.current_time: float = where_to_start
        self.adding: bool = is_it_adding


    def __str__(self) -> str:
        """
        Returns a string with class information so it can be printed later.
        """

        return (f"Current: {self.current_time} - Floor: {self.floor} - " +
                f"Ceiling: {self.ceil} - Is it adding: {self.adding}")


    def is_at_floor(self) -> bool:
        """
        Checks if the timer is at its lowest possible value.
        """

        return self.current_time == self.floor


    def is_at_ceiling(self) -> bool:
        """
        Checks if the timer is at its greatest possible value.
        """

        return self.current_time == self.ceil


    def count(self, how_much: float=1.0) -> None:
        """
        Advances the counting of the Timer, deducting if 'self.adding' is False, otherwise adding.
        """

        if self.adding:

            if self.current_time < self.ceil:

                self.current_time += how_much
        else:

            if self.current_time > self.floor:

                self.current_time -= how_much

        if any((self.current_time <= self.floor, self.current_time >= self.ceil)):

            self.adding = not self.adding


class Chronometer:
    """
    A chronometer to count up indefinitely.
    """

    def __init__(self, where_from: float=0.0, can_count: bool=True) -> None:
        """
        Initializes an instance of type 'Chronometer'.
        """

        self.initial_time: float = where_from
        self.current_time: float = self.initial_time
        self.splits: List[float] = []
        self.can_count: bool = can_count


    def __str__(self) -> str:
        """
        Shows the chronometer properties.
        """

        splits_info = ((f"\nSplit {ind + 1}:\t{split_time}"
                        for ind, split_time in enumerate(self.splits))
                       if self.splits else "N/A")

        return (f"Chronometer of: Initial Time: {self.initial_time} - " +
                f"Current Time: {self.current_time}" +
                f"\nSplits: {splits_info}")


    def start(self) -> None:
        """
        Starts the chronometer, allowing to start counting.
        """

        self.can_count = True


    def stop(self) -> None:
        """
        Stops the chronometer, forcing it to stop counting.
        """

        self.can_count = False


    def count(self, how_much: float=0.001) -> None:
        """
        Counts up by `how_much`.
        """

        if not self.can_count:
            return

        self.current_time += float(how_much)


    def split(self) -> None:
        """
        Appends the current time to the splits list.
        """

        self.splits.append(self.current_time)


    def reset(self) -> None:
        """
        Resets the chronometer back to its inital value.
        """

        self.current_time = self.initial_time
        self.splits.clear()
