import pygame

from crystal_engine.client.managers.NetworkManager import NetworkManager
from crystal_engine.client.managers.SceneManager import SceneManager
from crystal_engine.client.managers.UIManager import UIManager

class Game:
    def __init__(self, screensize) -> None:
        self.entities = []
        self.scenes = []
        self.managers = []

        self.running = True

        self.background_fill_colour = (0,0,0)
        
        pygame.init()

        self.screen = pygame.display.set_mode(screensize)

        self.load_managers()
        
    def loop(self, args=[]):
        events = pygame.event.get()
        pressed_keys = pygame.key.get_pressed()

        if self.background_fill_colour is not None:
            self.screen.fill(self.background_fill_colour)
        
        for loopable in self.entities + self.scenes + self.managers:
            if loopable is not None:
                loopable.loop(self.screen, events, pressed_keys, self, *args)

        for event in events:
            if event.type == pygame.QUIT:
                self.running = False

        return events, pressed_keys

    def load_managers(self):
        SceneManager(self)
        UIManager(self)
        NetworkManager(self)

    def load_manager(self, manager):
        manager()

    def unload_manager(self, manager):
        manager.unload()

    def end_loop(self, args=[]):
        pygame.display.update()