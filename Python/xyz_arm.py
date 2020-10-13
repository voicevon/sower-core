import sys
# sys.path.append('C:\\gitlab\\bot\\python\\reprap')  # on windows
# sys.path.append('/home/xm/gitrepo/bot/python/reprap')   # on linux
sys.path.append('/home/znkzjs/bot/python/reprap')   # on Jetson Nano

from reprap_arm import ReprapArm

import time

class XyzArm(ReprapArm):
    '''
    This robot arm is a human level robot.
    
    '''
    def __init__(self):
        ReprapArm.__init__(self)
        self.__current_x = 0
        self.__current_y = 0
        self.__current_z = 0

        # self.__feeding_buffer = FeedingBuffer()

    def __lift_warehouse(self):
        '''
        Wiring:  fan interface to control warehouse
        '''
        self.bridge_send_gcode_mcode('M106 S0')

    def __drop_warehouse(self):
        self.bridge_send_gcode_mcode('M106 S255')

    def __move_to_warehouse(self, row):
        y = 120 * row
        self.move_to_xyz(self.__current_x, y, self.__current_z)
        self.__current_y = y

    def pickup_from_warehouse(self):
        WAREHOUSE_MOVEMENT_TIME = 1.5   # when warehouse moves from bottom to top(or reverse), will cost some time. 

        self.__move_to_warehouse(3)
        self.__lift_warehouse()
        time.sleep(WAREHOUSE_MOVEMENT_TIME)
        self.__drop_warehouse()
        time.sleep(WAREHOUSE_MOVEMENT_TIME)


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
    if False:
        # moves a big squre
        while True:
            my_arm.move_to_xyz(0, 0, 0, 18000)
            my_arm.move_to_xyz(0, 280, 0, 18000)
            my_arm.move_to_xyz(180, 280, 0, 18000)
            my_arm.move_to_xyz(180, 0, 0, 18000)

    if True:
        # my_arm.pickup_from_warehouse()
        while True:
            my_arm.bridge_send_gcode_mcode('M106 S0')
            print('s0')
            time.sleep(2)
            my_arm.bridge_send_gcode_mcode('M106 S255')
            print('s80')
            time.sleep(3)

    

    # my_arm.Init_Marlin()
    # my_arm.Test2_home_sensor()
    # my_arm.set_fan_speed()


