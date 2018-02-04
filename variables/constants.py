class LanceConstant:
    def __init__(self, name, type, value):
        self.name = name
        self.type = type
        self.value = value

    def get(self):
        return self.value
