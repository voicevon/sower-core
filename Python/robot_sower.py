import sys
sys.path.append('/home/xm/gitrepo/pylib')
from app_config import AppConfig
from devices_helper import DevicesHelper
# from robot_servo_array import  ServoArrayDriver  # For Minghao solution only

from robot_sensors import RobotSensors
from robot_eye import RobotEye
from plate_Ver2 import Plate_Ver2
from robot_body import RobotBody



import Jetson.GPIO as GPIO
import board  # pip3 install adafruit-blinka
import busio
import threading


class RobotSower():
    # '''
    # There are two RobotBody()
    # each body have a set of XYZ_arm + servo_gates + current_plate,  we call it RobotBody
    # '''


    def __init__(self):
        helper = DevicesHelper()
        helper.serial_port_list_all()
        self.__eye = RobotEye()

        self.SOLUTION = AppConfig.robot_arms.servo_controller.solution
        if self.SOLUTION == 'minghao':
            self.__servos_minghao = ServoArrayDriver()
            port_name = helper.__get_serial_port_name_from_chip_name('USB2.0-Serial')
            self.__servos_minghao.connect_serial_port(port_name, 115200, echo_is_on=False)

        if self.SOLUTION == 'xuming':
            self.__current_plate = Plate_Ver2()
            self.__next_plate = Plate_Ver2() # Current version , we don't apply this.
            
            self.__sensors = RobotSensors(self.__on_new_row_enter)
            self.__sensors.setup()

            i2c_bus0=(busio.I2C(board.SCL_1, board.SDA_1,frequency=400000))
            xyz_arm_serial_port_name = helper.serial_port_from_location('1-2.1.1')
            self.__first_robot_body = RobotBody('first robot', xyz_arm_serial_port_name, i2c_bus0, 0x41)

            xyz_arm_serial_port_name = helper.serial_port_from_location('1-2.1.3')
            self.__second_robot_body = RobotBody('second robot',xyz_arm_serial_port_name, i2c_bus0, 0x42)  

    def on_eye_got_new_plate(self, plate_map):
        solution = AppConfig.robot_arms.servo_controller.solution
        if solution == 'minghao':
            self.__servos_minghao.send_new_platmap(plate_map)

        if solution == 'xuming':
            self.__current_plate.from_map(plate_map)

    def __new_row_enter_first_robot_body(self, row_id):
        if row_id >= 0:
            # get plan for the two rows of the first robot.
            plan = self.__current_plate.get_window_map(row_id)
            # execute the plan, This will update the plate map.
            action_map = self.__first_robot_body.execute_dropping(plan)
            self.__current_plate.update_dropping(action_map)

    def __new_row_enter_second_robot_body(self, row_id):
        if row_id >= 0:
            # get plan for the two rows of the first robot.
            plan = self.__current_plate.get_window_map(row_id)
            # execute the plan, This will update the plate map.
            action_map = self.__second_robot_body.execute_dropping(plan)
            self.__current_plate.update_dropping(action_map)

    def __on_new_row_enter(self):
        '''
        Should be a new thread.
        '''
        print("RobotSower.__on_new_row_enter()  comming row_id = ", self.__sensors.coming_row_id_to_first_robot_body, self.__sensors.coming_row_id_to_second_robot_body)
        row_id_first = self.__sensors.coming_row_id_to_first_robot_body
        row_id_second = self.__sensors.coming_row_id_to_second_robot_body
        if AppConfig.multi_thread:
            t1 = threading.Thread(target=self.__new_row_enter_first_robot_body, args=[row_id_first])
            t2 = threading.Thread(target=self.__new_row_enter_second_robot_body, args=[row_id_second])
            t1.start()
            t2.start()
        else:
            self.__new_row_enter_first_robot_body(row_id_first)
            self.__new_row_enter_second_robot_body(row_id_second)

        # can report the sower result here   
        

    def turn_on_light_fan_conveyor(self):
        self.__sensors.output_conveyor_motor(1)
        self.__sensors.output_vacuum_fan(1)
        self.__sensors.ouput_light(1)

    def spin_once(self): 
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
            self.__first_robot_body.spin_once(new_thread=AppConfig.multi_thread)
            self.__second_robot_body.spin_once(new_thread=AppConfig.multi_thread)
            self.__eye.spin_once()



if __name__ == "__main__":
    GPIO.cleanup()
    GPIO.setmode(GPIO.BOARD)

    t = RobotSower()
    t.turn_on_light_fan_conveyor()