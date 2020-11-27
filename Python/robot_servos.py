
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
        self.__kits = []
        #  [ (closed_angle, opened_angle), .... ]
        self.__servos_angle = [(40,70),(28,58),(0,30),(19,50),(18,45),(20,50),(20,50),(30,60),
                               (15,50),(23,60),(35,65),(8,40),(13,43),(35,65),(16,46),(30,60),
                            #    (40,70),(28,58),(0,30),(19,50),(18,45),(20,50),(20,50),(30,60),
                            #    (15,50),(23,60),(35,65),(8,40),(13,43),(35,65),(16,46),(30,60),
                              ]    
        self.__KIT_COUNT = int(len(self.__servos_angle) / 16)   

    def setup_gpio_i2cbus(self): 
        print("Initializing Servos")
        i2c_bus0=(busio.I2C(board.SCL_1, board.SDA_1,frequency=10000))
        print("Initializing ServoKit")
        kit_address = 0x40
        for i in range(0, self.__KIT_COUNT):
            kit = ServoKit(channels=16, i2c=i2c_bus0, address=kit_address)
            self.__kits.append(kit)
            print("initialied ", kit_address)
            kit_address += 1

    def append_planned_action(self, servos_action):
        # ??? 
        self.__planned_actions.append(servos_action)

    def set_servos_position(self, action_bytes):
        '''
        action_bytes: 
            bit == 1 will open the gate; bit == 0 ,will close the gate
            The length of action_bytes normally is 2/4/6/8... etc.
        '''
        for servo_id in range(0,self.__KIT_COUNT):
            kit_id = int(servo_id / 16)
            servo_id_in_kit = int(servo_id % 16)

            row_id = int(servo_id / 8)
            col_id = int(servo_id % 8)
            bit = action_bytes[row_id] & (1<<col_id)
            close_angle, oepn_angle = self.__servos_angle[servo_id]
            target_angle =  close_angle
            if bit:
                target_angle = oepn_angle
            self.__kits[kit_id].servo[servo_id_in_kit].angle = target_angle
                
if __name__ == "__main__":
    servos = Servos()
    servos.setup_gpio_i2cbus()
    
    test_id = 0x0
    while test_id == 0:
        gates = [0x00,0x01,0x00,0x00]  # bit 8 is always opened
        servos.set_servos_position(gates)
        print('closed')
        time.sleep(3)

        gates = [0x00,0x01,0x00,0x00]  # bit 0 is always closed
        servos.set_servos_position(gates)
        print('Opened ')
        time.sleep(3)        

    while test_id == 0x40:
        gates = [0x00,0x01,0x00,0x00]  # bit 8 is always opened
        servos.set_servos_position(gates)
        print('closed')
        time.sleep(3)

        gates = [0xfe,0xff,0xff,0xff]  # bit 0 is always closed
        servos.set_servos_position(gates)
        print('Opened ')
        time.sleep(3)    

    while test_id == 0x41:
        gates = [0x00,0x00,0x00,0x01]  # bit 8 is always opened
        servos.set_servos_position(gates)
        print('closed')
        time.sleep(3)

        gates = [0xff,0xff,0xfe,0xff]  # bit 0 is always closed
        servos.set_servos_position(gates)
        print('Opened ')
        time.sleep(3)    

    while test_id == 1:
        gates = [0x00,0x00]
        servos.set_servos_position(gates)
        print('closed')
        time.sleep(3)

        gates = [0xff,0xff]  
        servos.set_servos_position(gates)
        print('Opened ')
        time.sleep(3)
