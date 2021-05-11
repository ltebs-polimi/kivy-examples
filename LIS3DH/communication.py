"""@package communication
Documentation for this module.
 
More details.
"""
from kivy.event import EventDispatcher
from kivy.properties import NumericProperty, StringProperty # pylint: disable=no-name-in-module
import serial
import serial.tools.list_ports as list_ports
import struct
import threading
import time

from datetime import datetime

##
#   @brief          Data packet header.
#
DATA_PACKET_HEADER = 0xA0

##
#   @brief          Data packet tail.
#
DATA_PACKET_TAIL = 0xC0


"""
@brief Connection command.
"""
CONNECTION_CMD = 'v'

"""
@brief Start streaming command.
"""
START_STREAMING_CMD = 'b'

"""
@brief Stop streaming command.
"""
STOP_STREAMING_CMD = 's'

CONNECTION_STATE_DISCONNECTED = 0

CONNECTION_STATE_FOUND = 1

CONNECTION_STATE_CONNECTED = 2

FSR_PM_2G = 0
FSR_PM_4G = 1
FSR_PM_8G = 2
FSR_PM_16G = 3

MODE_NORMAL = 0
MODE_HIGH_RESOLUTION = 1
MODE_LOW_POWER = 2

class Singleton(type):
    ## Class used for Singleton pattern.
    #
    # This class allows to implement the Singleton pattern.
    # This pattern restricts the instantiation of a class
    # to one single instance. 
    # [Link](https://en.wikipedia.org/wiki/Singleton_pattern)
    #
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class KivySerial(EventDispatcher, metaclass=Singleton):
    """
    @brief Main class used for serial communication.
    
    This is the main class used to communicate with the serial port.
    It has @Singleton as a metaclass, so only one instance of this
    class exists throughout the application. 
    Automatic port discovery is implemented: it is not required to
    specify the serial port, as it is automatically detected by
    scanning all the available ports, and sending a known command
    to the port. If the expected response is detected, then 
    a connection with the serial port is carried out.
    """

    """
    @brief Connection status.

    0 means that the port is not connected, 1 that the
    port was found, 2 that a successfull connection was
    achieved.
    """
    connected = NumericProperty(0)

    """
    @brief Message to be shown.

    This is a string that is shown on the GUI for messages
    related to the serial communication.
    """
    message_string = StringProperty('')
    
    ## 
    #  @brief           Initialize the class.
    #
    #  @param[in]       baudrate: the desired baudrate for serial communication.
    #    
    def __init__(self, baudrate=115200):
        
        self.port_name = ""         # port name, set later when port is found
        self.baudrate = baudrate    # baudrate for serial communication
        self.is_streaming = False   # streaming status
        self.connected = 0          # connection status
        self.read_state = 0         # read state for data parser
        self.callbacks = []         # list of callbacks to be called when new data are available
        self.samples_counter = 0    # counter for samples received
        self.initial_time = 0       # time of first sample received
        self.timeout = 1        
        # Start thread for automatic port discovery
        find_port_thread = threading.Thread(target=self.find_port, daemon=True)
        find_port_thread.start()
        
    def add_callback(self, callback):
        """
        @brief Add callback.

        Add a callback to the list of callbacks
        that are called when a new sample is
        available.
        """
        if (callback not in self.callbacks):
            self.callbacks.append(callback)

    def find_port(self):
        """
        @brief Automatic port discovery.

        This function scans all the available COM ports
        to check if one of them is correct one. It does it
        by sending a #CONNECTION_CMD and checking if three
        $$$ are found in the response.
        """
        port_found = False
        time.sleep(5)
        while (not port_found):
            ports = list_ports.comports()
            if (len(ports) == 0):
                self.message_string = 'No ports found.. Check your connections'
                time.sleep(2)
            for port in ports:
                port_found = self.check_lis3dh_port(port.device)
                if (port_found):
                    self.port_name = port.device
                    if (self.connect() == 0):
                        break

    ## 
    #   @brief              Check if the port is the desired one.
    #
    #   This function sends a \ref CONNECTION_CMD to the port,
    #   and checks if three $$$ are found in the response from
    #   the port.
    #
    #   @param[in]          port_name: the name of the port to be checked
    #   @return             True if check was successfull, False otherwise.
    #    
    def check_lis3dh_port(self, port_name):
        self.message_string = 'Checking: {}'.format(port_name)
        try:
            port = serial.Serial(port=port_name, baudrate=self.baudrate, write_timeout=0, timeout=5)
            if (port.is_open):
                port.write(CONNECTION_CMD.encode('utf-8'))
                time.sleep(2)
                received_string = ''
                while (port.in_waiting > 0):
                    received_string += port.read().decode('utf-8', errors='replace')
                if ('$$$' in received_string):
                    self.message_string = 'Device found on port: {}'.format(port_name)
                    self.connected = CONNECTION_STATE_FOUND
                    port.close()
                    time.sleep(2)
                    return True
        except serial.SerialException:
            return False
        except ValueError:
            return False
        return False

    def connect(self):
        """
        @brief Connect to the port.
        """
        try:
            self.port = serial.Serial(port=self.port_name, baudrate=self.baudrate, timeout=self.timeout)
        except serial.SerialException:
            self.message_string = f'Error when opening port'
            return -1
        if (self.port.is_open):
                self.message_string = f'Device connected at {self.port_name}'
                self.connected = CONNECTION_STATE_CONNECTED
                return 0
        return -1

    def on_connected(self, instance, value):
        """
        @brief Callback for change in connected property.
        """
        if (value == 0):
            self.is_streaming = False
            self.message_string = 'Device disconnected'

    def start_streaming(self):
        """
        @brief Start streaming data from serial port.
        """
        if (self.connected == CONNECTION_STATE_CONNECTED):
            if (not (self.is_streaming)):
                self.message_string = 'Starting data streaming'
                self.port.write(START_STREAMING_CMD.encode('utf-8'))
                self.is_streaming = True
                self.read_state = 0
                self.skipped_bytes = 0
                read_thread = threading.Thread(target=self.collect_data)
                read_thread.daemon = True
                read_thread.start()
                self.samples_counter = 0
        else:
            self.message_string = 'Device is not connected.'

    def collect_data(self):
        """
        @brief Collect data from serial port while streaming is active.
        """
        while(self.is_streaming):
            self.skipped_bytes = 0
            packet = self.read_serial_binary()
            for callback in self.callbacks:
                callback(packet)
            self.update_sample_rate()
    
    def update_sample_rate(self):
        if (self.samples_counter == 0):
            print('0 samples')
            self.initial_time = datetime.now()
        elif (self.samples_counter == 1):
            print('1 sample')
            now = datetime.now()
            self.diff = (datetime.now() - self.initial_time).total_seconds()
            self.sample_rate = 1 / (datetime.now() - self.initial_time).total_seconds() 
            print(self.sample_rate)
            self.initial_time = now
        else:
            diff = (datetime.now() - self.initial_time).total_seconds()
            self.diff = self.diff + (diff - self.diff) / (self.samples_counter+1)
            self.sample_rate = (self.samples_counter+1) / self.diff
            self.message_string = f'Samples: {self.samples_counter:6d} | Sample Rate: {self.sample_rate:4.2f}'
        self.samples_counter += 1


    def read_serial_binary(self, max_bytes_to_skip=3000):
        '''
        @brief Serial data parser.

        Parses incoming data packet into a Sample
        Incoming packet structure:
        START_BYTE(1)| X_AXIS(2) | Y_AXIS(2) | Z_AXIS(2) | END_BYTE (1)
        '''
        for rep in range(max_bytes_to_skip):
            if (self.read_state == 0):
                b = self.port.read(1)
                if (len(b) > 0):
                    # Header byte
                    b = struct.unpack('B', b)[0]
                    if (b == DATA_PACKET_HEADER):
                        print(f'Skipped {rep} bytes')
                        rep = 0
                        self.read_state = 1
            elif (self.read_state == 1):
                # Get three bytes
                data = self.port.read(6)
                data = struct.unpack('6B', data)
                x_data = data[0:2]
                y_data = data[2:4]
                z_data = data[4:]
                x_data = self.convert_acc_data(x_data)
                y_data = self.convert_acc_data(y_data)
                z_data = self.convert_acc_data(z_data)
                self.read_state = 2
            elif (self.read_state == 2):
                tail_byte = self.port.read(1)
                tail_byte = struct.unpack('B', tail_byte)[0]
                if (tail_byte == DATA_PACKET_TAIL):
                    print('Packet complete')
                    packet = LIS3DHDataPacket(x_data, y_data, z_data)
                    self.read_state = 0
                    return packet

    def convert_acc_data(self, data):
        temp_data = data[0] << 8 | data[1]
        print(temp_data)
        if (temp_data & 0x8000):
            # We have a negative number
            temp_data = 0xFFFF - temp_data
            temp_data = temp_data + 1
            temp_data = - temp_data
            temp_data = temp_data >> 6
            temp_data = temp_data * 4
        else:
            temp_data = temp_data >> 6
            temp_data = temp_data * 4
        return temp_data / 1000.

    def stop_streaming(self):
        """
        @brief Stop streaming from the serial port.
        """
        self.message_string = 'Stopped streaming data'
        self.port.write(STOP_STREAMING_CMD.encode('utf-8'))
        self.is_streaming = False
    
    def update_sample_rate_on_board(self, value):
        sample_rate_dict = {
            '1 Hz' : '0',
            '10 Hz': '1',
            '25 Hz': '2',
            '100 Hz': '3',
            '200 Hz': '4'
        }
        if (self.port.is_open):
            try:
                print(sample_rate_dict[value])
                self.port.write(sample_rate_dict[value].encode('utf-8'))
            except:
                self.message_string = "Could not update sample rate"

    ##
    #   @brief          Get if serial port is connected.
    #   @return         True if connected, False otherwise
    def is_connected(self):
        if (self.connected == CONNECTION_STATE_CONNECTED):
            return True
        else:
            return False

class LIS3DHDataPacket():
    def __init__(self, x_data, y_data, z_data):
        self.x_data = x_data
        self.y_data = y_data
        self.z_data = z_data

    def get_x_data(self):
        return self.x_data

    def get_y_data(self):
        return self.y_data

    def get_z_data(self):
        return self.z_data
