import threading
from robot_servo_kit import SowerServoKit
from robot_xyz_arm import XyzArm

class RobotBody():

    def __init__(self, xyz_arm_serial_port_name, i2c_bus, kit_address):
        self.xyz_arm = XyzArm(kit_address)
        self.xyz_arm.connect_and_init(xyz_arm_serial_port_name)
        self.xyz_arm.home_y_x()
        self.servos_kit = SowerServoKit(i2c_bus, kit_address)
        self.seed_buffer = [0xff,0xff]   #bit defination: 0 = BLANK,  1 = OCCUPIED
        self.__debug_kit_address = kit_address
        
    def make_plan_and_execute(self, window_map):
        '''
        
        '''
        drop_plan=[0x00,0x00]   #bit defination: 0 = No drop,   1 = dropped
        drop_plan[0] = self.seed_buffer[0] & ~window_map[0]
        drop_plan[1] = self.seed_buffer[1] & ~window_map[1]
        self.servos_kit.execute_dropping(drop_plan)
        self.seed_buffer[0] &= ~drop_plan[0]
        self.seed_buffer[1] &= ~drop_plan[1]
        return drop_plan

    def get_first_empty_cell(self):
        '''
            return row_id, col_id. 
            If no empty cell, return -1, -1 
        '''
        for row_id in range(0,2):
            for col_id in range(7,-1,-1):
                if self.seed_buffer[row_id] & 1<<col_id == 0:
                    # print('RobotBody.get_first_empty_cell() instance,row,col=',self.__debug_kit_address, row_id,col_id)
                    return row_id, col_id
        return -1,-1


    def __spin_once(self):
        row_id, col_id = self.get_first_empty_cell()
        if row_id >=0:
            self.xyz_arm.pickup_from_warehouse(col_id)
            self.xyz_arm.place_to_cell(row=row_id, col=col_id)
            self.seed_buffer[row_id] += 1<<col_id
    
    def spin_once(self, new_thread=True):
        if new_thread:
            t1 = threading.Thread(target=self.__spin_once)
            t1.start()
            return
        self.__spin_once()
