


class app_config:
    class path:
        text_color = '/home/xm/gitrepo/ros_marlin_bridge/perfect'
    class server:
        class mqtt:
            broker_addr = 'voicevon.vicp.io'
            port = 1883
            username = 'von'
            password = 'von1970'

    class robot_arm:
        name = 'Cartisian'

    class robot_eye:
        camera_index = 0

if __name__ == "__main__":
    global_config = app_config
    s1 = global_config.robot_arm.name
    print(s1)