import pygame
from crystal_engine.client.util.Loopable import Loopable

class Animation(Loopable):
    def __init__(self, image_paths=[]):
        self.current_frame = 0

        self.frames = []
        self.flipped_frames = []
        
        self.image_paths = image_paths

        super().__init__()

    def load(self):
        self.frames = []

        for path in self.image_paths:
            self.frames.append(pygame.image.load(path).convert_alpha())

    def load_flipped_frames(self):
        for frame in self.frames:
            self.flipped_frames.append(pygame.transform.flip(frame, True, False).convert_alpha())

    def add_flipped_frames_to_animation(self, left=True):
        if left:
            self.frames = self.flipped_frames + self.frames
        else:
            self.frames = self.frames + self.flipped_frames

    def get_frame(self):
        return self.frames[self.current_frame]

    def loop(self, screen, *args):
        super().loop(screen, *args)

        self.current_frame += 1

        if self.current_frame == len(self.frames):
            self.current_frame = 0