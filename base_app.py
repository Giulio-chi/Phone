import pygame

from abc import ABC, abstractmethod

class BaseApp(ABC):
    def __init__(self, set_active_app, keys_utilities=None, scope=None, scope_to_utilities=None):
        pygame.init()
        self.screen_size = (300, 600)
        self.screen = pygame.Surface(self.screen_size)

        self.clock = pygame.time.Clock()
        self.mouse = pygame.mouse.get_pos()

        self.set_active_app = set_active_app
        
        if scope is not None:
            self.scope = scope

        if scope_to_utilities is not None:
            self.scope_to_utilities = scope_to_utilities

        if keys_utilities is not None:
            self.keys_utilities = keys_utilities

        else:
            if scope_to_utilities is not None and scope is not None:
                self.keys_utilities = scope_to_utilities[scope]

            else:
                raise AttributeError('keys_utilities must be provided or scope_to_utilities and scope must be set.', self)

    @abstractmethod
    def run(self, display):
        ...

    @abstractmethod
    def events(self, event):
        ...

    def get_relative_mouse_pos(self, display):
        self.mouse = pygame.mouse.get_pos()
        self.mouse = (
            self.mouse[0] - display.get_width() // 2 + self.screen.get_width() // 2,
            self.mouse[1] - display.get_height() // 2 + self.screen.get_height() // 2
        )