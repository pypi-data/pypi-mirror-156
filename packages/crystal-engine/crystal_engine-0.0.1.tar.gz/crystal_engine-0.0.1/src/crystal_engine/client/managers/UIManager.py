from crystal_engine.client.managers.Manager import Manager

class UIManager(Manager):
    def __init__(self, game) -> None:
        super().__init__(game)

        self.ui_elements = []

    def loop(self, screen, *args):
        super().loop(screen, *args)

        for ui_element in self.ui_elements:
            ui_element.loop(screen, *args)

    def add_ui_element(self, ui_element):
        self.ui_elements.append(ui_element)