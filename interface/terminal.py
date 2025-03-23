import pygame
import typing
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
    def __init__(
        self, screen_size: typing.Tuple[int, int], terminal_size: typing.Tuple[int, int]
    ):
        super().__init__(screen_size)
        self.font = pygame.font.SysFont("Monaco", 12)

        # Run once
        self.change_history: typing.List[InterfaceAction] = []
        self.history_index = 0

        # Run every draw frame
        self.renders: typing.List[RenderAction] = []

        self.terminal_size = terminal_size
        self.foreground_color = (255, 255, 255)
        self.background_color = (0, 0, 0)

        self.on_draw = []
        self.on_update = []

        self.cursor = Cursor((0, 0), (self.font.size(" ")[0], self.font.size(" ")[1]))

    def update(self, dt: int, events: typing.List[pygame.event.Event]):
        self.cursor.update(dt)

        for action in self.change_history[self.history_index :]:
            self.history_index += 1
            action.act()

    def draw(self, screen: pygame.Surface):
        # TODO: Add scrollbars

        self.fill((0, 0, 0))

        for render in self.renders:
            render.act(self)

        self.cursor.draw(self)

        screen.blit(self, (0, 0))
