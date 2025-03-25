import pygame
from pygame import *
import sys


class Window:
    FPS = 30

    def __init__(self):
        pygame.init()
        pygame.freetype.init()
        self.clock = pygame.time.Clock()
        # TODO: Make resizable
        # TODO: Save window size to cache and reload on program start
        width, height = 640, 480
        self.screen = pygame.display.set_mode((width, height))
        self.running = True
        pygame.display.set_caption("Willow")

        self.on_update = []
        self.on_draw = []
        self.on_exit = []

    def run(self) -> None:
        while self.running:
            self.update()
            self.draw()
        self._exit()

    def _exit(self) -> None:
        for callable in self.on_exit:
            callable()
        pygame.quit()
        sys.exit()

    def update(self) -> None:
        dt = self.clock.tick(Window.FPS)

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False

        for callable in self.on_update:
            callable(dt, events)

    def draw(self) -> None:
        self.screen.fill((0, 0, 0))

        for callable in self.on_draw:
            callable(self.screen)

        pygame.display.flip()
