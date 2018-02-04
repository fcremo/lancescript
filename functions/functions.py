class LanceFunction:
    def __init__(self, name, parameters, code):
        self.name = name
        self.parameters = parameters
        self.code = code


class LanceFunctionParameter:
    def __init__(self, name, type, is_array=False):
        self.name = name
        self.type = type
        self.is_array = is_array
