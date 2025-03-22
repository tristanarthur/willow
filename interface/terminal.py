import pygame
import typing
from interface.actions import InterfaceAction


class Cursor:
    def __init__(
        self,
        position: typing.Tuple[int, int],
        size: typing.Tuple[int, int],
        color: typing.Tuple[int, int, int] = (255, 255, 255),
    ):
        self.position = position
        self.blink_speed = 500  # ms
        self.size = size
        self.color = color
        self._visible = True
        self._blink_timer = 0
        self._blink_speed = 500  # ms

    def update(self, dt: int):
        self._blink_timer += dt
        if self._blink_timer >= self._blink_speed:
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
        # TODO Change this to enable variable column and row sizes
        self.terminal_matrix = [
            [" " for _ in range(terminal_size[0])] for _ in range(terminal_size[1])
        ]
        self.cursor = Cursor((0, 0), (self.font.size(" ")[0], self.font.size(" ")[1]))

    def update(self, dt: int, events: typing.List[pygame.event.Event]):
        self.cursor.update(dt)

    def draw(self, screen: pygame.Surface):
        # TODO: Add scrollbars

        self.fill((0, 0, 0))

        for y, row in enumerate(self.terminal_matrix):
            for x, char in enumerate(row):
                char_surface = self.font.render(char, False, (255, 255, 255))
                char_width, char_height = self.font.size(char)
                self.blit(char_surface, (x * char_width, y * char_height))

        self.cursor.draw(self)

        screen.blit(self, (0, 0))

    def write(self, char: str):
        self.terminal_matrix[self.cursor.position[1]][self.cursor.position[0]] = char
        self.cursor.position = (self.cursor.position[0] + 1, self.cursor.position[1])

        # Wrap text
        if self.cursor.position[0] >= len(
            self.terminal_matrix[self.cursor.position[1]]
        ):
            self.cursor.position = (0, self.cursor.position[1] + 1)

        # Move to next line
        if self.cursor.position[1] >= len(self.terminal_matrix):
            self.cursor.position = (0, 0)

    def act(self, actions: typing.List[InterfaceAction]):
        for action in actions:
            action.act()
