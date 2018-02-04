from exceptions.exceptions import UninitializedValueAccess, OutOfBoundsAccess


class LanceScriptScalarVariable:
    def __init__(self, name, type, value=None):
        self.name = name
        self.type = type
        self.value = value

    def get(self):
        if self.value is None:
            raise UninitializedValueAccess("Access to uninitialized variable {}".format(self.name))

        return self.value

    def set(self, val):
        self.value = val


class LanceScriptArrayVariable:
    def __init__(self, name, type, size, default_value=None):
        self.name = name
        self.type = type
        self.size = size
        self.values = [LanceScriptScalarVariable(name+"_"+str(i), type, default_value) for i in range(size)]

    def get(self, idx):
        if not 0 <= idx < self.size:
            raise OutOfBoundsAccess("Out of bounds read access to index {} of variable {}".format(idx, self.name))

        return self.values[idx].get()

    def set(self, idx, val):
        if not 0 <= idx < self.size:
            raise OutOfBoundsAccess("Out of bounds write access to index {} of variable {}".format(idx, self.name))

        self.values[idx].set(val)
