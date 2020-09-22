
class Cave():
    def __init__(self):
        self.id = 0
        self.col = 0
        self.row = 0

    def from_id(self, id):
        self.id = id
        self.row = id / 8
        self.col = id % 8


class Plate():
    def __init__(self):
        self.id = 0
        self.cols = 8
        self.rows = 16


class SowerBuffer():
    def __init__(self):
        self.cols = 8
        self.rows = 3

