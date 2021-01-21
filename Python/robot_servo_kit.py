
#  Jetson Expansion Header Tool
#       sudo /opt/nvidia/jetson-io/jetson-io.py
#           from: https://www.jetsonhacks.com/2020/05/04/spi-on-jetson-using-jetson-io/


# List I2C devices
#   ls /dev/i2c*
# List I2C address on device 0
#   i2cdetect -r -y 0

#  https://learn.adafruit.com/16-channel-pwm-servo-driver/python-circuitpython
import time
import board  # pip3 install adafruit-blinka
import busio
from adafruit_servokit import ServoKit  # pip3 install adafruit-circuitpython-servokit

# To Install
#   $ git clone https://github.com/JetsonHacksNano/ServoKit
#   $ cd ServoKit
#   $ ./installServoKit.sh
# To verify
#   i2cdetect -r -y 0
# 
# import adafruit_pca9685 # sudo pip3 install adafruit-circuitpython-pca9685 ???? Looks like this is a micro-python libery
# from adafruit_servokit import ServoKit  
# import adafruit_motor.servo
# View GPIO pinout
#   sudo /opt/nvidia/jetson-io/jetson-io.py

# Try to create an I2C device
  

class SowerServoKit():
    # https://pypi.org/project/Jetson.GPIO/
    # https://www.jetsonhacks.com/2019/07/22/jetson-nano-using-i2c/
    # https://elinux.org/Jetson/I2C
    def __init__(self, i2c_bus, kit_address):
        self.__gates_angle_0x41 = [(19,35,49),(23,35,53),(15,30,45),(14,30,44),(16,35,66),(16,30,46),(17,30,47),(22,40,52),
                    (17,30,47),(22,35,52),(36,50,66),(12,30,42),(15,30,45),(21,40,51),(16,30,46),(27,40,57)]
        self.__gates_angle_0x42 = [(40,45,70),(24,33,54),(18,22,48),(10,24,45),(18,24,48),(18,28,48),(18,27,48),(29,37,59),
                    (15,25,45),(22,34,52),(32,42,62),(4,14,34),(10,20,40),(35,40,65),(10,18,40),(30,38,60)]

        self.__kit = ServoKit(channels=16, i2c=i2c_bus, address=kit_address)

        self.__on_off_angles = []
        if kit_address == 0x41:
            self.__on_off_angles = self.__gates_angle_0x41
        elif kit_address == 0x42:
            self.__on_off_angles = self.__gates_angle_0x42
        else:
            print('[WARN][SowerServoKit]::__init__() wrong kit_address = %i' %kit_address)


    def __set_single_servo_on_off(self, servo_id, action):
        '''
        TODO 
            Need try exception. to avoid hardware "OSError: [Error 121] Remote I/O error"

        '''
        close_angle, idle_angle, oepn_angle = self.__on_off_angles[servo_id]
        target_angle = idle_angle
        if action == 'OPEN':
            target_angle = oepn_angle
        elif action =='CLOSE':
            target_angle = close_angle
        elif action != 'IDLE':
            print('[WARN][SowerServoKit]::__set_single_servo_on_off(wrong action parameter) = %s' %action)

        # print('SowerServoKit(). __set_single_servo_on_off() ', servo_id, target_angle)
        self.__kit.servo[servo_id].angle = target_angle

    def set_single_servo_on_off(self,row_id, col_id,action='CLOSE'):
        servo_id = row_id * 8 + col_id
        self.__set_single_servo_on_off(servo_id,action)

    def execute_dropping(self, planned_drop_map):
        for row_id in range(0,2):
            row_action = planned_drop_map[row_id]
            for col_id in range(0,8):
                is_to_open = row_action & 1<<col_id
                if is_to_open:
                    single_action = 'OPEN'
                else:
                    single_action = 'CLOSE'

                self.set_single_servo_on_off(row_id=row_id, col_id=col_id, action=single_action)
                
if __name__ == "__main__":

    test_id = 2
    test_address = 0x42
    i2c_bus0=(busio.I2C(board.SCL_1, board.SDA_1,frequency=400000))

    servos = SowerServoKit('second servo kit',i2c_bus0, test_address)
    print('init is ok')
    row = 0
    col = 4


    while test_id == 1:
        for row in range(0,2):
            for col in range(0,8):
                servos.set_single_servo_on_off(row, col_id=col, action='CLOSE')
                print('closed')
                time.sleep(1)

                servos.set_single_servo_on_off(row, col_id=col, action='OPEN')
                print('Opened ')
                time.sleep(1)   

    while test_id == 2:
        for row in range(0,2):
            for col in range(0,8):
                servos.set_single_servo_on_off(row,col, action='IDLE')
        time.sleep(1)

   