
class Cell():
    def __init__(self):
        self.id = 0
        self.col = 0
        self.row = 0
        self.value = 0   # 0 = empty, 1 = one seed, 2 = two seeds

    def from_id(self, id):
        self.id = id
        self.row = id / 8
        self.col = id % 8

    def from_col_row(self, col_id, row_id):
        self.col = col_id
        self.row = row_id
        self.id = col_id + row_id * 8   # TODO: instead const with config 


class Plate():
    def __init__(self):
        self.id = 0
        self.cols = 8
        self.rows = 16
        self.layout = [([0] * self.cols) for i in range(self.rows)]

    def find_empty_cell(self):
        for col in range(0, self.cols):
            for row in range(0, self.rows):
                if self.layout[col, row] == 0:
                    # This is an empty cell
                    empty_cell = Cell()
                    empty_cell.from_id

        return empty_cell


class FeedingBuffer(Plate):
    def __init__(self):
        self.id = 0 
        self.cols = 8
        self.rows = 3
