
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
                topics = {
                                'sower/arm/': 12,
                                "sower/outside/system/state" : 11,
                                "sower/eye/outside/width": 11,
                                "sower/eye/outside/height": 11,
                                "sower/eye/inside/camera/config_file": 11,
                                "sower/eye/inside/camera/trigger_mode": 11,
                                "sower/eye/inside/camera/trigger_type": 11,
                                "sower/eye/inside/camera/aestate": 11,
                                "sower/eye/inside/camera/exposure_time": 11,
                                "sower/eye/inside/detect/threshold_r": 11,
                                "sower/eye/inside/detect/threshold_g": 11,
                                "sower/eye/inside/detect/threshold_b": 11,
                                "sower/eye/inside/detect/threshold_size": 11,
                                "sower/eye/inside/detect/display": 11,
                                "sower/eye/inside/detect/roi/x": 11,
                                "sower/eye/inside/detect/roi/y": 11,
                                "sower/eye/inside/detect/roi/width": 11,
                                "sower/eye/inside/detect/roi/height": 11,
                                "sower/eye/inside/camera/soft_trigger": 11,
                                }

    class robot_arms:
        class xyz_arm:
            name = 'Cartisian'
            port_name = 'dev/ttyUSB0'
            baudrate = 115200
        
        class servo_controller:
            solution = 'xuming'

            # solution = 'minghao'
            port_name = 'dev/ttyUSB1'
            baudrate = 115200

    class robot_eye:
        camera_index = 0

    class chessboard:
        rows_count = 3
        cols_count = 8

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
 