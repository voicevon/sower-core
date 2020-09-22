import serial, time


class ServoArrayDriver():

    class ServoArray_serial:
        '''
        Hand shaking with controller through serial port.
        '''
        def __init__(self, portname, baudrate):
            self.__serialport = serial.Serial()
            self.__serialport.port = portname
            self.__serialport.baudrate = baudrate
            self.__serialport.timeout = 1
            self.__serialport.writeTimeout = 2
        
            self.__counter = 0
            self.__echo_is_on = False

        def Connect(self):
            self.__serialport.open()
            if self.__echo_is_on:
                print ('Reprap_host::Serial port is opened.')
            while True:
                xx = self.__serialport.readline()
                mm = bytes.decode(xx)
                if (mm == ''):
                    break

        def set_echo_on(self, is_on):
            self.__echo_is_on = is_on

        def SendCommandCode(self, raw_gcode):
            self.__counter += 1
            self.__serialport.write(str.encode(raw_gcode +'\r\n'))
            if self.__echo_is_on:
                print ('>>> %s' % raw_gcode)
            got_ok = False
            while not got_ok:
                response_a = self.__serialport.readline()
                response = bytes.decode(response_a)
                if(response == 'ok\n'):
                    got_ok = True
                    if self.__echo_is_on:
                        print ('OK')
                elif (response ==''):
                    rospy.sleep(0.1)
                elif self.__echo_is_on:
                    print("<<< " + response)

    def __init__(self):
        pass

    def __send_command(self, code):
        waitting_mil_second = 0
        while waitting_mil_second < 600:
            waitting_mil_second += 1
            if True:
                return 'the response here'
        return 'No response'

    def update_caves(self, caves):
        pass
