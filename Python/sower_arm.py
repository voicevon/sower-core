import sys
sys.path.append('C:\\gitlab\\bot\\python\\reprap')  # on windows
# sys.path.append('/home/xm/gitrepo/bot/python/reprap') # on linux

from reprap_arm import ReprapArm

class SowerArm(ReprapArm):
    '''
    This robot arm is a human level robot.
    
    '''
    pass

if __name__ == "__main__":
    my_arm = SowerArm()
    my_arm.connect_to_marlin()
    my_arm.Init_Marlin()
    my_arm.Test2_home_sensor()
