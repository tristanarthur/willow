import pygame
import typing

import pygame.freetype
from interface.actions import InterfaceAction, RenderAction


class Cursor:
    def __init__(
        self,
        position: typing.Tuple[int, int],
        size: typing.Tuple[int, int],
        color: typing.Tuple[int, int, int] = (255, 255, 255),
    ):
        self.position = position
        self.size = size
        self.color = color
        self._visible = True
        self._blink_timer = 0
        self._blink_speed = 500  # ms  Set 0 for no blink

    def update(self, dt: int):
        self._blink_timer += dt
        if self._blink_speed > 0 and self._blink_timer >= self._blink_speed:
            self._visible = not self._visible
            self._blink_timer = 0

    def draw(self, screen: pygame.Surface):
        if self._visible:
            pygame.draw.rect(
                screen,
                self.color,
                (
                    self.position[0] * self.size[0],
                    self.position[1] * self.size[1],
                    self.size[0],
                    self.size[1],
                ),
            )


class TerminalInterface(pygame.Surface):
    DEFAULT_FOREGROUND_COLOR = (255, 255, 255)
    DEFAULT_BACKGROUND_COLOR = (0, 0, 0)

    def __init__(
        self, screen_size: typing.Tuple[int, int], terminal_size: typing.Tuple[int, int]
    ):
        super().__init__(screen_size)
        self.font = pygame.freetype.SysFont("Monaco", 12)
        self.font.origin = True

        # Run once
        self.change_history: typing.List[InterfaceAction] = []
        self.history_index = 0

        # Run every draw frame
        self.renders: typing.List[RenderAction] = []

        self.terminal_size = terminal_size
        self.foreground_color = self.DEFAULT_FOREGROUND_COLOR
        self.background_color = self.DEFAULT_BACKGROUND_COLOR
        self.bold = False
        self.italic = False
        self.underline = False

        self.on_draw = []
        self.on_update = []

        self.cursor = Cursor((0, 0), (self.font.get_rect(" ").width, self.font.get_rect(" ").height))

    def update(self, dt: int, events: typing.List[pygame.event.Event]):
        self.cursor.update(dt)

        for action in self.change_history[self.history_index :]:
            self.history_index += 1
            action.act()

    def draw(self, screen: pygame.Surface):
        # TODO: Add scrollbars

        self.fill((0, 0, 0))

        if self.bold:
            self.font.set_bold(True)
        if self.italic:
            self.font.set_italic(True)
        if self.underline:
            self.font.set_underline(True)

        for render in self.renders:
            render.act()

        self.cursor.draw(self)

        screen.blit(self, (0, 0))
