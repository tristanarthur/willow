from abc import ABC, abstractmethod
import typing
import pygame
import pygame.freetype
import stransi
from dataclasses import dataclass


ActionArguments = typing.Tuple[typing.Any, ...]


class InterfaceAction(ABC):
    def __init__(
        self,
        terminal_interface: "TerminalInterface",
        instruction: stransi.instruction.Instruction,
    ):
        self.interface = terminal_interface
        self.instruction = instruction

    @abstractmethod
    def act(self) -> None:
        pass


class RenderAction(InterfaceAction):
    def __init__(
        self,
        terminal_interface: "TerminalInterface",
        instruction: stransi.instruction.Instruction,
    ):
        super().__init__(terminal_interface, instruction)

    @abstractmethod
    def act(self, surface: pygame.Surface) -> None:
        pass


class CharacterRenderAction(RenderAction):
    def __init__(
        self,
        terminal_interface: "TerminalInterface",
        character: str,
        font: pygame.freetype.Font,
        position: typing.Tuple[int, int],
        foreground_color: typing.Tuple[int, int, int],
        background_color: typing.Tuple[int, int, int],
    ):
        super().__init__(terminal_interface, character)
        self.character = character
        self.font = font
        self.position = position
        self.position = (
            self.position[0] * self.font.get_rect(" ").width,
            self.position[1] * self.font.get_sized_height(12) + 12,
        )
        self.foreground_color = foreground_color
        self.background_color = background_color

    def act(self):
        style = pygame.freetype.STYLE_NORMAL
        if self.interface.bold:
            style = pygame.freetype.STYLE_STRONG
        if self.interface.italic:
            style = pygame.freetype.STYLE_OBLIQUE
        if self.interface.underline:
            style = pygame.freetype.STYLE_UNDERLINE
        self.font.render_to(
            surf=self.interface,
            dest=self.position,
            text=self.character,
            fgcolor=self.foreground_color,
            bgcolor=self.background_color,
            style=style,
        )


@dataclass
class InsertCharacterInstruction(stransi.instruction.Instruction):
    character: str


class InsertCharacterAction(InterfaceAction):
    def __init__(
        self,
        terminal_interface: "TerminalInterface",
        instruction: InsertCharacterInstruction,
    ):
        super().__init__(terminal_interface, instruction)

    def _handle_newline(self):
        move_cursor_instruction = stransi.cursor.SetCursor(
            move=stransi.cursor.CursorMove.to(0, self.interface.cursor.position[1] + 1)
        )
        MoveCursorAction(self.interface, move_cursor_instruction).act()

    def act(self):
        self.instruction: InsertCharacterInstruction
        if self.instruction.character.encode("utf-8") == b"\x07":
            return
        if self.instruction.character == "\n":
            self._handle_newline()
            return

        self.interface.renders.append(
            CharacterRenderAction(
                self.interface,
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
        instruction: stransi.cursor.SetCursor,
    ):
        super().__init__(terminal_interface, instruction)

    def act(self):
        self.instruction: stransi.cursor.SetCursor
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


class SetColorAction(InterfaceAction):
    def __init__(
        self,
        terminal_interface: "TerminalInterface",
        instruction: stransi.color.SetColor,
    ):
        super().__init__(terminal_interface, instruction)

    def act(self):
        self.instruction: stransi.color.SetColor
        if self.instruction.role == stransi.color.ColorRole.FOREGROUND:
            foreground_color = [
                int(channel * 255) for channel in self.instruction.color.rgb
            ]
            self.interface.foreground_color = tuple(foreground_color)
        elif self.instruction.role == stransi.color.ColorRole.BACKGROUND:
            background_color = [
                int(channel * 255) for channel in self.instruction.color.rgb
            ]
            self.interface.background_color = tuple(background_color)


class SetAttributeAction(InterfaceAction):
    def __init__(
        self,
        terminal_interface: "TerminalInterface",
        instruction: stransi.attribute.SetAttribute,
    ):
        super().__init__(terminal_interface, instruction)

    def act(self):
        self.instruction: stransi.attribute.SetAttribute
        if self.instruction.attribute is stransi.attribute.Attribute.NORMAL:
            self.interface.bold = False
            self.interface.italic = False
            self.interface.underline = False
            self.interface.foreground_color = self.interface.DEFAULT_FOREGROUND_COLOR
            self.interface.background_color = self.interface.DEFAULT_BACKGROUND_COLOR
        elif self.instruction.attribute is stransi.attribute.Attribute.BOLD:
            self.interface.bold = True
        elif self.instruction.attribute is stransi.attribute.Attribute.ITALIC:
            self.interface.italic = True
        elif self.instruction.attribute is stransi.attribute.Attribute.UNDERLINE:
            self.interface.underline = True


class DoNothingAction(InterfaceAction):
    def __init__(
        self,
        terminal_interface: "TerminalInterface",
        instruction: stransi.instruction.Instruction,
    ):
        super().__init__(terminal_interface, instruction)

    def act(self):
        pass
