

class Simulator:
    def __init__(self):
        self.apogee: float = 0

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]
