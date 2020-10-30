
from datetime import datetime
import cv2


class app_config:

    class path:
        text_color = '/home/xm/gitrepo/ros_marlin_bridge/perfect'

    class server:
        class mqtt:
            broker_addr = 'voicevon.vicp.io'
            port = 1883
            username = 'von'
            password = 'von1970'
            class subscript_topics:
                topics = ['sower/arm/',
                                 'sower/eye/',
                                 ]

    class robot_arms:
        name = 'Cartisian'
        port_name = 'dev/ttyUSB0'
        baudrate = 115200

        class servo_controller:
            port_name = 'dev/ttyUSB1'
            baudrate = 115200

    class robot_eye:
        camera_index = 0

    class layout:
        class seed_box:
            center_x = 100
            center_y = 200

        class feeding_house:
            top_left = 300
            bottom_right = 400
            rows = 3
            cols = 8


class CvDebugger():
    @staticmethod
    def show_debug_image(window_name, soure_img, debug_text):
        if app_config.robot_eye.board_scanner.show_board_image:
            cp = soure_img.copy()
            debug_text += '  ' + datetime.now().strftime('%s')
            cv2.putText(cp, debug_text, (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1)
            cv2.imshow(window_name, cp)
            cv2.waitKey(1)


if __name__ == "__main__":
    global_config = app_config
    s1 = global_config.robot_arm.name
    print(s1)

    global_config.robot_arm.name = 'test'
    s1 = global_config.robot_arm.name
    print(s1)
 