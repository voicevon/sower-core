import sys
# sys.path.append('C:\\gitlab\\bot\\python\\reprap')  # on windows
# sys.path.append('/home/xm/gitrepo/bot/python/reprap')   # on linux
sys.path.append('/home/znkzjs/bot/python/reprap')   # on Jetson Nano

from reprap_arm import ReprapArm

import time

class XyzArm(ReprapArm):
    '''
    This robot arm is a human level robot.
    Warehouse postion: When idle, it's at bottom.
    '''
    def __init__(self):
        ReprapArm.__init__(self)
        self.__placed_counter = 0
        self.__mqtt = None

    def __get_xy_from_col_row(self, col, row):
        '''
        if row == -1, will return warehouse of X

        From manual calibration:  col,row :(0,0)  maps to x,y (30,20)
        '''
        x = 30 + col * 32
        y = 20 + row * 32
        if col == -1:
            x = 180
        return x, y

    def lift_warehouse(self):
        '''
        Wiring:  fan interface to control warehouse
        '''
        self.bridge_send_gcode_mcode('M106 S255')

    def drop_warehouse(self):
        self.bridge_send_gcode_mcode('M106 S0')

    def __move_to_warehouse(self, row):
        x, y = self.__get_xy_from_col_row(-1, row)
        self.move_to_xyz(x, y,speed_mm_per_min=18000)
        self.__current_y = y

    def pickup_from_warehouse(self, row):
        WAREHOUSE_MOVEMENT_TIME = 1.5   # when warehouse moves from bottom to top(or reverse), will cost some time. 

        self.__move_to_warehouse(row)
        self.lift_warehouse()
        time.sleep(WAREHOUSE_MOVEMENT_TIME)
        self.drop_warehouse()
        time.sleep(WAREHOUSE_MOVEMENT_TIME)


    def place_to_cell(self, col, row):
        '''
        A certain path, that based on cell position.
        Basically, The path looks like this, total composed from 3 segments

         <-----------------------------
        |
        | 
        |------------------------------>
        '''
        x, y = self.__get_xy_from_col_row(col,row)
        self.move_to_xyz (x , y )
        self.move_to_xyz(x , y + 32)
        self.move_to_xyz(180, y+32 )

        self.__placed_counter += 1
        self.__mqtt.publish('sower/xyzarm/placed_counter', self.__placed_counter)

    def setup(self, feeding_buffer, mqtt):
        self.__feeding_buffer = feeding_buffer
        self.__mqtt = mqtt
        for col in range(0,3):
            for row in range(0,8):
                print('pickup and place %i %i' %(col,row))
                self.pickup_from_warehouse(row)
                self.place_to_cell(col,row)


    def init_and_home(self):
        self.connect_to_marlin()
        self.allow_cold_extrusion()
        self.home(home_y=True)
        self.home(home_x=True)

    def start_with_new_thread(self):
        self.__on_my_own_thread = True
        t = threading(self.__main_task)
        t.start

    def main_loop(self):
        # This is mainly for debugging. do not use while loop in this function!
        # For better performance, invoke start_with_new_thread() instead.
        self.__main_task()

    def __main_task(self):
        # Check feeding_buffer is there any cave is empty
        col, row  = self.__target_plate.find_empty_cell()
        if col is not None:
            self.__robot.place_to_cell(col, row)
            self.__robot.pickup_from_warehouse(row)
        pass

    def calibrate_col_row(self, col, row):
        x, y = self.__get_xy_from_col_row(col, row)
        # x, y = (180,180)
        self.move_to_xyz(x, y, speed_mm_per_min=18000)

if __name__ == "__main__":
    my_arm = XyzArm()
    my_arm.init_and_home()
    if False:
        my_arm.calibrate_col_row(2,7)

    if False:
        # moves a big squre
        while True:
            my_arm.move_to_xyz(0, 0, 0, 18000)
            my_arm.move_to_xyz(0, 280, 0, 18000)
            my_arm.move_to_xyz(180, 280, 0, 18000)
            my_arm.move_to_xyz(180, 0, 0, 18000)

    if False:
        # test warehouse
        while True:
            my_arm.lift_warehouse()
            time.sleep(2)
            my_arm.drop_warehouse()
            time.sleep(5)

    if True:
        while True:
            my_arm.pickup_from_warehouse(7)
            my_arm.place_to_cell(0,7)
            time.sleep(5)

            my_arm.pickup_from_warehouse(5)
            my_arm.place_to_cell(1,5)
            time.sleep(5)

            my_arm.pickup_from_warehouse(0)
            my_arm.place_to_cell(2,0)
            time.sleep(5)


    # my_arm.Init_Marlin()
    # my_arm.Test2_home_sensor()
    # my_arm.set_fan_speed()


