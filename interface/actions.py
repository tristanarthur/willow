from abc import ABC, abstractmethod
import typing


class InterfaceAction(ABC):
    def __init__(self, terminal_interface: "TerminalInterface"):
        self.interface = terminal_interface

    @abstractmethod
    def act(self) -> None:
        pass


class InsertCharacterAction(InterfaceAction):
    def __init__(self, terminal_interface: "TerminalInterface", char: str):
        super().__init__(terminal_interface)
        self.char = char

    def act(self):
        self.interface.write(self.char)


class MoveCursorAction(InterfaceAction):
    def __init__(
        self,
        terminal_interface: "TerminalInterface",
        position: typing.Tuple[int, int] = None,
        x_is_relative: bool = True,
        y_is_relative: bool = True,
    ):
        super().__init__(terminal_interface)
        self.x_is_relative = x_is_relative
        self.y_is_relative = y_is_relative
        self.position = position

    def act(self):
        x = self.interface.cursor_position[0]
        y = self.interface.cursor_position[1]
        if self.x_is_relative:
            x += self.position[0]
        else:
            x = self.position[0]
        if self.y_is_relative:
            y += self.position[1]
        else:
            y = self.position[1]

        self.interface.cursor_position = (x, y)

    @staticmethod
    def to_position(
        terminal_interface: "TerminalInterface", position: typing.Tuple[int, int]
    ):
        return MoveCursorAction(terminal_interface, position, False)

    @staticmethod
    def up(terminal_interface: "TerminalInterface", n: int = 1):
        return (MoveCursorAction(terminal_interface, (0, -n), True, True),)

    @staticmethod
    def down(terminal_interface: "TerminalInterface", n: int = 1):
        return MoveCursorAction(terminal_interface, (0, n), True, True)

    @staticmethod
    def forward(terminal_interface: "TerminalInterface", n: int = 1):
        return MoveCursorAction(terminal_interface, (n, 0), True, True)

    @staticmethod
    def back(terminal_interface: "TerminalInterface", n: int = 1):
        return MoveCursorAction(terminal_interface, (-n, 0), True, True)

    @staticmethod
    def next_line(terminal_interface: "TerminalInterface", n: int = 1):
        return MoveCursorAction(terminal_interface, (0, n), False, True)

    @staticmethod
    def previous_line(terminal_interface: "TerminalInterface", n: int = 1):
        return MoveCursorAction(terminal_interface, (0, -n), False, True)

    @staticmethod
    def horizontal_absolute(terminal_interface: "TerminalInterface", x: int):
        return MoveCursorAction(terminal_interface, (x, 0), False, True)


class DoNothingAction(InterfaceAction):
    def __init__(self, terminal_interface: "TerminalInterface"):
        super().__init__(terminal_interface)

    def act(self):
        pass
