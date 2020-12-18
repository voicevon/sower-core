
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
    def __init__(self, name, i2c_bus, kit_address, on_off_angles):
        self.__name = name
        self.__kit = ServoKit(channels=16, i2c=i2c_bus, address=kit_address)
        self.__on_off_angles = on_off_angles

    def __set_single_servo_on_off(self, servo_id, action):
        close_angle, oepn_angle = self.__on_off_angles[servo_id]
        target_angle = close_angle
        if action == 'OPEN':
            target_angle = oepn_angle
        else:
            print('wrong parameter at flag= %s' %action)

        # print(servo_id, target_angle)
        self.__kit.servo[servo_id].angle = target_angle

    def set_single_servo_on_off(self,row_id, col_id,action='CLOSE'):
        servo_id = row_id * 8 + col_id
        self.__set_single_servo_on_off(servo_id,action)

                
if __name__ == "__main__":
    i2c_bus0=(busio.I2C(board.SCL_1, board.SDA_1,frequency=400000))
    gates_angle = [0x00, 0x00]
    servos = SowerServoKit('first servo kit',i2c_bus0,0x42, gates_angle)
    
    test_id = 1  

    while test_id == 1:
        servos.set_single_servo_on_off(0,1,'CLOSE')
        print('closed')
        time.sleep(3)

        servos.set_single_servo_on_off(0,1,'OPEN')
        print('Opened ')
        time.sleep(3)        

   