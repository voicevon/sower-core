
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
  

class Servos_action():
    '''
    From right to left, named byte_0, byte_1, byte_2
    '''
    def __init__(self):
        self.row_id = 0
        self.byte_0 = 0
        self.byte_1 = 0
        self.byte_2 = 0


class Servos():
    # https://pypi.org/project/Jetson.GPIO/
    # https://www.jetsonhacks.com/2019/07/22/jetson-nano-using-i2c/
    # https://elinux.org/Jetson/I2C
    def __init__(self):
        self.last_finished_row = 0
        self.__planned_actions = []

    def setup_gpio_i2cbus(self):
        print("Initializing Servos")
        i2c_bus0=(busio.I2C(board.SCL_1, board.SDA_1))
        print("Initializing ServoKit")
        self.__kit_0 = ServoKit(channels=16, i2c=i2c_bus0, address=0x40)
        print("initialied 0x40")
        self.__kit_1 = ServoKit(channels=16, i2c=i2c_bus0, address=0x41)
        # kit[0] is the bottom servo
        # kit[1] is the top servo
        print("initialied 0x41")
        # print("Done initializing")
        # while True:
        #     # sweep = range(0,180)
        #     #for degree in sweep:
        #     kit.servo[0].angle=180

    def append_planned_action(self, servos_action):
        # ??? 
        self.__planned_actions.append(servos_action)

    def output_i2c(self, row_id):
        # https://learn.adafruit.com/circuitpython-libraries-on-linux-and-the-nvidia-jetson-nano?view=all#i2c-sensors-devices
        self.__kit.servo[0].angle =  100

    def update_servo_angle(self, servo_id, target_angle):
        kit = self.__kit_0
        if servo_id >= 16:
            kit = self.__kit_1
            servo_id -= 16
        print(servo_id)

        kit.servo[servo_id].angle = target_angle

# kit = ServoKit(channels=8)
 
# kit.servo[0].angle = 180
# kit.continuous_servo[1].throttle = 1
# time.sleep(1)
# kit.continuous_servo[1].throttle = -1
# time.sleep(1)
# kit.servo[0].angle = 0
# kit.continuous_servo[1].throttle = 0

if __name__ == "__main__":
    servos = Servos()
    servos.setup_gpio_i2cbus()
    while True:
        for s in range(0,32):
            servos.update_servo_angle(s,0)
            print('.')
            # for a in range(0,180, 60):
            #     servos.update_servo_angle(s, a)
            #     print('.', end='')
            # time.sleep(0.05)
            # print('')
        time.sleep(2)

        for s in range(0,32):
            servos.update_servo_angle(s,180)
            print('*')
            # for a in range(180,0, -60):
            #     servos.update_servo_angle(s, a)
            #     print('.', end='')
            # time.sleep(0.05)
            # print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
        time.sleep(2)