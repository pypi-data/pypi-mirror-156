import os

class ResourceLocation(str):
    def __init__(self, path="") -> None:
        self.path = path

    def __str__(self) -> str:
        return os.path.join(__file__, "..", self.path)

    @staticmethod
    def multiple(*paths):
        return [ResourceLocation(path) for path in paths]