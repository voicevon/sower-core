import sys
# sys.path.append('C:\\gitlab\\bot\\python\\reprap')  # on windows
# sys.path.append('/home/xm/gitrepo/bot/python/reprap')   # on linux
sys.path.append('/home/znkzjs/bot/python/reprap')   # on Jetson Nano

from reprap_arm import ReprapArm

class XyzArm(ReprapArm):
    '''
    This robot arm is a human level robot.
    
    '''
    def __init__(self):
        ReprapArm.__init__(self)
        # self.__feeding_buffer = FeedingBuffer()

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

    def init_and_home(self):
        self.connect_to_marlin()
        self.allow_cold_extrusion()
        self.home(home_y=True)
        self.home(home_x=True)

if __name__ == "__main__":
    my_arm = XyzArm()
    my_arm.init_and_home()
    while True:
        my_arm.move_to_xyz(0, 0, 0, 18000)
        my_arm.move_to_xyz(0, 280, 0, 18000)
        my_arm.move_to_xyz(180, 280, 0, 18000)
        my_arm.move_to_xyz(180, 0, 0, 18000)


    

    # my_arm.Init_Marlin()
    # my_arm.Test2_home_sensor()
    # my_arm.set_fan_speed()


