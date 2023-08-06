from crystal_engine.client.managers.Manager import Manager

class SceneManager(Manager):
    def __init__(self, game) -> None:
        super().__init__(game)

        self.current_scene = None

    def loop(self, screen, *args):
        super().loop(screen, *args)

        if self.current_scene is not None:
            self.current_scene.loop(screen, *args)

    def set_scene(self, scene):
        self.current_scene = scene