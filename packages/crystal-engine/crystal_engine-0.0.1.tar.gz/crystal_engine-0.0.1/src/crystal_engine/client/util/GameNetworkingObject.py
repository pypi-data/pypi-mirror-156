class GameNetworkingObject:
    def __init__(self):
        pass

    def add_field(self, field_name, field_value):
        setattr(self, field_name, field_value)

    def set_field(self, field_name, field_value):
        setattr(self, field_name, field_value)