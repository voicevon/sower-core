from reprap_robot_arm import ReprapRobot
from plate_and_cell import Cell, Plate, FeedingBuffer


class HumanLevelRobot(ReprapRobot):
    
    def __init__(self):
        ReprapRobot.__init__(self)
        self.__feeding_buffer = FeedingBuffer()

    def pickup_from_warehouse(self):
        self.goto('warehouse')
        self.warehouse_move_up()
        self.eef_pick_up()
        self.warehouse_move_down()

    def place_to_cell(self, cell_name):
        # a certain path, that based on cell position
        cell = Cell()
        cell.from_name(cell_name)
        x, y = (1, 2)
        self.__move_to(x + 1, y - 2)
        self.__move_to(x + 3, y - 4)
        self.__move_to(x + 5, y - 6)
        self.__move_to(x + 7, y - 8)

    def setup(self, feeding_buffer):
        self.__feeding_buffer = feeding_buffer


if __name__ == "__main__":
    test = HumanLevelRobot()
