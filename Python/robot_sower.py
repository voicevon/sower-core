from robot_sensors import RobotSensors
from robot_xyz_arm import XyzArm
from robot_servo_array import  ServoArrayDriver  # For Minghao solution only
from robot_sensors import Servos   # For Xuming solution only
from chessboard import  g_chessboard, ChessboardCell, CHESSBOARD_CELL_STATE
from plate import Plate, PlateCell, PLATE_CELL_STATE, PLATE_STATE

from app_config import AppConfig

# import serial.tools.list_ports
import sys
sys.path.append('/home/xm/pylib')
from devices_helper import DevicesHelper


class RobotBody():

    def __init__(self, serial_port_name, do_init_marlin=False, do_home=False):
        self.xyz_arm = XyzArm()
        self.servo_gate = Servos()
    
        if do_init_marlin:
            self.xyz_arm.setup_and_home(serial_port_name)
        if do_home:
            self.xyz_arm.home_y_x()   


class RobotSower():
    # '''
    # This is the hard robot, will take the plan and execute it.
    # There are two RobotBody()
    # each body have a set of XYZ_arm + servo_gates, we call it RobotBody
    # '''


    def __init__(self, do_init_marlin=False, do_home=False):

        self.SOLUTION = AppConfig.robot_arms.servo_controller.solution
        if self.SOLUTION == 'minghao':
            self.__servos_minghao = ServoArrayDriver()
            port_name = self.__get_serial_port_name_from_chip_name('USB2.0-Serial')
            self.__servos_minghao.connect_serial_port(port_name, 115200, echo_is_on=False)

        if self.SOLUTION == 'xuming':
            self.__sensors = RobotSensors(self.__on_new_plate_enter, self.__on_new_row_enter)
            self.__sensors.setup()
            self.__current_plate = Plate()
            self.__next_plate = Plate()

        helper = DevicesHelper()
        helper.serial_port_list_all()

        port_name = helper.serial_port_from_location('1-2.1.2')
        print('first arm, port_name =', port_name)
        self.__robot_body_first = RobotBody(port_name,do_init_marlin, do_home)

        port_name = helper.serial_port_from_location('1-2.1.2')
        self.__robot_body_second = RobotBody(port_name, do_home)

    def on_eye_got_new_plate(self, plate_array):
        solution = AppConfig.robot_arms.servo_controller.solution
        if solution == 'minghao':
            new_map = plate_array
            self.__servos_minghao.send_new_platmap(new_map)

        if solution == 'xuming':
            plate_map = plate_array
            self.__next_plate.from_map(plate_map)

    def __on_new_plate_enter(self):
        map = self.__next_plate.get_plate_map()
        self.__current_plate.from_map(map)

    def __on_new_row_enter(self):
        g_chessboard.execute_plan()
        g_chessboard_need_a_new_plan = True
        # reload plan from where??
        # g_chessboard.reload_plan()

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
    # GPIO.setmode(GPIO.BOARD)
    t = RobotSower(do_init_marlin=True,do_home=True)

    t.turn_on_light_fan_conveyor()