from abc import ABC, abstractmethod
import typing
import pygame


ActionArguments = typing.Tuple[typing.Any, ...]


class InterfaceAction(ABC):
    def __init__(self, terminal_interface: "TerminalInterface", args: ActionArguments=()):
        self.interface = terminal_interface
        self.args = args

    @abstractmethod
    def act(self) -> None:
        pass


class RenderAction(InterfaceAction):
    def __init__(self, terminal_interface: "TerminalInterface", args: ActionArguments=()):
        super().__init__(terminal_interface, args)

    @abstractmethod
    def act(self, surface: pygame.Surface) -> None:
        pass

class CharacterRenderAction(RenderAction):
    def __init__(
        self,
        character: str,
        font: pygame.font.Font,
        position: typing.Tuple[int, int],
        foreground_color: typing.Tuple[int, int, int],
        background_color: typing.Tuple[int, int, int],
    ):
        self.character = character
        self.font = font
        self.position = position
        self.foreground_color = foreground_color
        self.background_color = background_color

    def act(self, surface: pygame.Surface):
        char_surface = self.font.render(self.character, False, self.foreground_color, self.background_color)
        char_width, char_height = self.font.size(self.character)
        surface.blit(char_surface, (self.position[0] * char_width, self.position[1] * char_height))


class InsertCharacterAction(InterfaceAction):
    def __init__(self, terminal_interface: "TerminalInterface", args: ActionArguments=()):
        super().__init__(terminal_interface, args)

    def validate(self):
        if len(self.args) != 1 and not isinstance(self.args[0], str):
            raise ValueError("InsertCharacterAction must have exactly one string argument")

    def act(self):
        self.interface.renders.append(
            CharacterRenderAction(
                self.args[0], 
                self.interface.font,
                self.interface.cursor.position, 
                self.interface.foreground_color, 
                self.interface.background_color
            )
        )
        MoveCursorAction.forward(self.interface, (1,)).act()


class MoveCursorAction(InterfaceAction):
    def __init__(
        self,
        terminal_interface: "TerminalInterface",
        args: ActionArguments=(),
        x_is_relative: bool = True,
        y_is_relative: bool = True,
    ):
        super().__init__(terminal_interface, args)
        self.x_is_relative = x_is_relative
        self.y_is_relative = y_is_relative


    def act(self):
        x = self.interface.cursor.position[0]
        y = self.interface.cursor.position[1]
        if self.x_is_relative:
            x += self.args[0]
        else:
            x = self.args[0]
        if self.y_is_relative:
            y += self.args[1]
        else:
            y = self.args[1]

        if x > self.interface.terminal_size[0]:
            x = 0
            y += 1

        self.interface.cursor.position = (x, y)

    @staticmethod
    def to_position(
        terminal_interface: "TerminalInterface", position: ActionArguments = (1, 1,)
    ):
        return MoveCursorAction(terminal_interface, position, False, False)
    
    @staticmethod
    def up(terminal_interface: "TerminalInterface", n: ActionArguments = (1,)):
        return MoveCursorAction(terminal_interface, (0, int(-n[0])), True, True)

    @staticmethod
    def down(terminal_interface: "TerminalInterface", n: ActionArguments = (1,)):
        return MoveCursorAction(terminal_interface, (0, int(n[0])), True, True)

    @staticmethod
    def forward(terminal_interface: "TerminalInterface", n: ActionArguments = (1,)):
        return MoveCursorAction(terminal_interface, (int(n[0]), 0), True, True)

    @staticmethod
    def back(terminal_interface: "TerminalInterface", n: ActionArguments = (1,)):
        return MoveCursorAction(terminal_interface, (-int(n[0]), 0), True, True)

    @staticmethod
    def next_line(terminal_interface: "TerminalInterface", n: ActionArguments = (1,)):
        return MoveCursorAction(terminal_interface, (0, int(n[0])), False, True)

    @staticmethod
    def previous_line(terminal_interface: "TerminalInterface", n: ActionArguments = (1,)):
        return MoveCursorAction(terminal_interface, (0, int(-n[0])), False, True)

    @staticmethod
    def horizontal_absolute(terminal_interface: "TerminalInterface", x: ActionArguments = (1,)):
        return MoveCursorAction(terminal_interface, (int(x[0]), 0), False, True)


class DoNothingAction(InterfaceAction):
    def __init__(self, terminal_interface: "TerminalInterface", args: ActionArguments=()):
        super().__init__(terminal_interface, args)

    def act(self):
        pass
