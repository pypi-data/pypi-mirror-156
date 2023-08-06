from crystal_engine.client.util.Loopable import Loopable

class Manager(Loopable):
    def __init__(self, game) -> None:
        self.id = len(game.managers)
        self.game = game

        self.game.managers.append(self)

        setattr(self.game, self.__class__.__name__, self)
        
        pass

    def update_manager(self):
        self.game.managers[self.id] = self

    def unload(self):
        self.game.managers[self.id] = None