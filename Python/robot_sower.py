from robot_sensors import RobotSensors
from robot_xyz_arm import XyzArm
from robot_servo_array import  ServoArrayDriver  # For Minghao solution only
# from robot_sensors import Servos   # For Xuming solution only
from chessboard import  g_chessboard, ChessboardCell, CHESSBOARD_CELL_STATE
from plate import Plate, PlateCell, PLATE_CELL_STATE, PLATE_STATE

from app_config import AppConfig

# import serial.tools.list_ports
import sys
sys.path.append('/home/xm/pylib')
from devices_helper import DevicesHelper
from robot_servo_kit import SowerServoKit

import Jetson.GPIO as GPIO
import board  # pip3 install adafruit-blinka
import busio
class RobotBody():

    def __init__(self, body_name, xyz_arm_serial_port_name, i2c_bus, kit_address):
        self.__body_name = body_name
        self.xyz_arm = XyzArm()
        self.xyz_arm.connect_and_init(xyz_arm_serial_port_name)
        self.xyz_arm.home_y_x()
        self.servos_kit = SowerServoKit(body_name, i2c_bus, kit_address)
        self.seed_buffer = [0x00,0x00]   #bit defination: 0 = BLANK,  1 = OCCUPIED
        
    def execute_dropping(self, dropping_plan):
        action_map=[0x00,0x00]   #bit defination: 0 = No drop,   1 = dropped
        action_map[0] = self.seed_buffer & dropping_plan[0]
        action_map[1] = self.seed_buffer & dropping_plan(1)
        return action_map

class RobotSower():
    # '''
    # This is the hard robot, will take the plan and execute it.
    # There are two RobotBody()
    # each body have a set of XYZ_arm + servo_gates, we call it RobotBody
    # '''


    def __init__(self):
        helper = DevicesHelper()
        helper.serial_port_list_all()

        self.SOLUTION = AppConfig.robot_arms.servo_controller.solution
        if self.SOLUTION == 'minghao':
            self.__servos_minghao = ServoArrayDriver()
            port_name = helper.__get_serial_port_name_from_chip_name('USB2.0-Serial')
            self.__servos_minghao.connect_serial_port(port_name, 115200, echo_is_on=False)

        if self.SOLUTION == 'xuming':
            # self.__sensors = RobotSensors(self.__on_new_plate_enter, self.__on_new_row_enter)
            self.__sensors = RobotSensors(self.__on_new_row_enter)
            self.__sensors.setup()
            self.__current_plate = Plate()
            self.__next_plate = Plate()



            i2c_bus0=(busio.I2C(board.SCL_1, board.SDA_1,frequency=400000))
            xyz_arm_serial_port_name = helper.serial_port_from_location('1-2.1.1')
            self.__first_robot_body = RobotBody('first robot', xyz_arm_serial_port_name, i2c_bus0, 0x41)


            xyz_arm_serial_port_name = helper.serial_port_from_location('1-2.1.3')
            self.__second_robot_body = RobotBody('second robot',xyz_arm_serial_port_name, i2c_bus0, 0x42)  



    def on_eye_got_new_plate(self, plate_array):
        solution = AppConfig.robot_arms.servo_controller.solution
        if solution == 'minghao':
            new_map = plate_array
            self.__servos_minghao.send_new_platmap(new_map)

        if solution == 'xuming':
            plate_map = plate_array
            self.__next_plate.from_map(plate_map)

    def __on_new_row_enter(self):
        print("RobotSower.__on_new_row_enter()  comming row_id = ", self.__sensors.coming_row_id_to_first_robot_body, self.__sensors.coming_row_id_to_second_robot_body)
        row_id = self.__sensors.coming_row_id_to_first_robot_body
        if row_id >= 0:
            # get plan for the two rows of the first robot.
            plan = self.__current_plate.get_window_map(row_id)
            # execute the plan, This will update the plate map.
            action_map = self.__first_robot_body.execute_dropping(plan)
            self.__current_plate.executed_dropping(action_map)

        row_id = self.__sensors.coming_row_id_to_second_robot_body
        if row_id >= 0:
            # get plan for the two rows of the first robot.
            plan = self.__current_plate.get_window_map(row_id)
            # execute the plan, This will update the plate map.
            action_map = self.__second_robot_body.execute_dropping(plan)
            self.__current_plate.executed_dropping(action_map)


        # can report the sower result here   
        

    def turn_on_light_fan_conveyor(self):
        self.__sensors.output_conveyor_motor(1)
        self.__sensors.output_vacuum_fan(1)
        self.__sensors.ouput_light(1)

    def spin_once(self):
        # self.__xyz_arm.test_minghao()
        # print('-------------------------------------------------------------------------------------------------------------------------')

        solution = AppConfig.robot_arms.servo_controller.solution
        if solution == 'minghao':
            row_id, col_id = self.__servos_minghao.get_first_empty_cell()
            if row_id >= 0:
                # TODO: this is a long time processing, should start a new thread 
                # there is an empty cell
                self.__xyz_arm_first.pickup_from_warehouse(col_id)
                self.__xyz_arm_first.place_to_cell(row_id, col_id)
                # update map and send new map to Minghao's subsystem
                print('after place_to_cell row_id, col_id ', row_id, col_id )
                self.__servos_minghao.update_chessmap_from_xyz_arm(row_id=row_id, col_id=col_id)
            self.__servos_minghao.spin_once()
            # self.__servos_minghao.update_chessmap_from_minghao_controller()

        if solution == 'xuming':
            return
            if g_chessboard_need_a_new_plan:    
                g_chessboard.loadplan()
                g_chessboard_need_a_new_plan = False
            
            row_id, col_id = g_chessboard.get_first_empty_cell()
            if row_id >= 0:
                # TODO: this is a long time processing, should start a new thread 
                self.__xyz_arm_first.pickup_from_warehouse(row_id)
                self.__xyz_arm_first.place_to_cell(row_id, col_id)
                g_chessboard.set_one_cell(row_id, col_id)

if __name__ == "__main__":
    GPIO.cleanup()
    GPIO.setmode(GPIO.BOARD)

    t = RobotSower()
    t.turn_on_light_fan_conveyor()