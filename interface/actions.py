from abc import ABC, abstractmethod
import typing
import pygame
import stransi
from dataclasses import dataclass



ActionArguments = typing.Tuple[typing.Any, ...]


class InterfaceAction(ABC):
    def __init__(
        self, terminal_interface: "TerminalInterface", instruction: stransi.instruction.Instruction
    ):
        self.interface = terminal_interface
        self.instruction = instruction

    @abstractmethod
    def act(self) -> None:
        pass


class RenderAction(InterfaceAction):
    def __init__(
        self, terminal_interface: "TerminalInterface", instruction: stransi.instruction.Instruction
    ):
        super().__init__(terminal_interface, instruction)

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
        char_surface = self.font.render(
            self.character, False, self.foreground_color, self.background_color
        )
        char_width, char_height = self.font.size(self.character)
        surface.blit(
            char_surface,
            (self.position[0] * char_width, self.position[1] * char_height),
        )

@dataclass
class InsertCharacterInstruction(stransi.instruction.Instruction):
    character: str


class InsertCharacterAction(InterfaceAction):
    def __init__(
        self, terminal_interface: "TerminalInterface", instruction: InsertCharacterInstruction
    ):
        super().__init__(terminal_interface, instruction)

    def validate(self):
        if len(self.instruction.args) != 1 and not isinstance(self.instruction.args[0], str):
            raise ValueError(
                "InsertCharacterAction must have exactly one string argument"
            )

    def act(self):
        self.interface.renders.append(
            CharacterRenderAction(
                self.instruction.character,
                self.interface.font,
                self.interface.cursor.position,
                self.interface.foreground_color,
                self.interface.background_color,
            )
        )
        move_cursor_instruction = stransi.cursor.SetCursor(
            move=stransi.cursor.CursorMove(
                x=1,
                y=0,
                relative=True,
            )
        )
        MoveCursorAction(self.interface, move_cursor_instruction).act()


class MoveCursorAction(InterfaceAction):
    def __init__(
        self,
        terminal_interface: "TerminalInterface",
        instruction: stransi.cursor.Instruction,
    ):
        super().__init__(terminal_interface, instruction)


    def act(self):
        x = self.interface.cursor.position[0]
        y = self.interface.cursor.position[1]
        if self.instruction.move.relative:
            x += self.instruction.move.x
            y += self.instruction.move.y
        else:
            x = self.instruction.move.x
            y = self.instruction.move.y

        if x > self.interface.terminal_size[0]:
            x = 0
            y += 1

        self.interface.cursor.position = (x, y)


class DoNothingAction(InterfaceAction):
    def __init__(
        self, terminal_interface: "TerminalInterface", instruction: stransi.instruction.Instruction
    ):
        super().__init__(terminal_interface, instruction)

    def act(self):
        pass
