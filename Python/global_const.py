
class app_config:

    class path:
        text_color = '/home/xm/gitrepo/ros_marlin_bridge/perfect'

    class server:
        class mqtt:
            broker_addr = 'voicevon.vicp.io'
            port = 1883
            username = 'von'
            password = 'von1970'

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


if __name__ == "__main__":
    global_config = app_config
    s1 = global_config.robot_arm.name
    print(s1)

    global_config.robot_arm.name = 'test'
    s1 = global_config.robot_arm.name
    print(s1)  