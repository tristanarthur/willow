import pygame
import typing
from interface.actions import InterfaceAction


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
        self.cursor_position = (0, 0)
        self.cursor_blink_speed = 500  # ms
        self._cursor_blink_timer = 0
        self._cursor_visible = True

    def update(self, dt: int, events: typing.List[pygame.event.Event]):
        # Blink cursor
        self._cursor_blink_timer += dt
        if self._cursor_blink_timer >= self.cursor_blink_speed:
            self._cursor_visible = not self._cursor_visible
            self._cursor_blink_timer = 0

    def draw(self, screen: pygame.Surface):
        # TODO: Add scrollbars

        self.fill((0, 0, 0))

        for y, row in enumerate(self.terminal_matrix):
            for x, char in enumerate(row):
                char_surface = self.font.render(char, False, (255, 255, 255))
                char_width, char_height = self.font.size(char)
                self.blit(char_surface, (x * char_width, y * char_height))

        if self._cursor_visible:
            self.draw_cursor(screen)

        screen.blit(self, (0, 0))

    def draw_cursor(self, screen: pygame.Surface):
        print(self.cursor_position)
        pygame.draw.rect(
            self,
            (0, 255, 255),
            (
                self.cursor_position[0] * self.font.size(" ")[0],
                self.cursor_position[1] * self.font.size(" ")[1],
                self.font.size(" ")[0],
                self.font.size(" ")[1],
            ),
        )

    def write(self, char: str):
        self.terminal_matrix[self.cursor_position[1]][self.cursor_position[0]] = char
        self.cursor_position = (self.cursor_position[0] + 1, self.cursor_position[1])

        # Wrap text
        if self.cursor_position[0] >= len(
            self.terminal_matrix[self.cursor_position[1]]
        ):
            self.cursor_position = (0, self.cursor_position[1] + 1)

        # Move to next line
        if self.cursor_position[1] >= len(self.terminal_matrix):
            self.cursor_position = (0, 0)

    def act(self, actions: typing.List[InterfaceAction]):
        for action in actions:
            action.act()
