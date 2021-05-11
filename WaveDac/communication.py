import serial
import serial.tools.list_ports as list_ports
import threading
from kivy.properties import NumericProperty, StringProperty
from kivy.event import EventDispatcher
import time
import struct

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class KivySerial(EventDispatcher, metaclass=Singleton):
    connected = NumericProperty(defaultvalue=0)
    message_string = StringProperty('')
    sample_rate = NumericProperty(0)

    def __init__(self):
        self.port_name = ""
        self.baudrate = 115200
        self.is_streaming = False
        self.connected = 0
        self.read_state = 0
        self.callbacks = []
        find_port_thread = threading.Thread(target=self.find_port, daemon=True)
        find_port_thread.start()
    
    def add_callback(self, callback):
        if (callback not in self.callbacks):
            self.callbacks.append(callback)

    def find_port(self):
        mip_port_found = False
        while (not mip_port_found):
            ports = list_ports.comports()
            for port in ports:
                mip_port_found = self.check_mip_port(port.device)
                if (mip_port_found):
                    self.port_name = port.device
                    if (self.connect() == 0):
                        break

    def check_mip_port(self, port_name):
        self.message_string = 'Checking: {}'.format(port_name)
        try:
            port = serial.Serial(port=port_name, baudrate=self.baudrate)
            if (port.is_open):
                port.write('v'.encode('utf-8'))
                time.sleep(2)
                received_string = ''
                while (port.in_waiting > 0):
                    received_string += port.read().decode('utf-8', errors='replace')
                if ('$$$' in received_string):
                    self.message_string = 'Device found on port: {}'.format(port_name)
                    port.close()
                    time.sleep(1)
                    self.connected = 1
                    return True
        except serial.SerialException:
            return False
        except ValueError:
            return False
        return False

    def connect(self):
        self.port = serial.Serial(port=self.port_name, baudrate=self.baudrate)
        if (self.port.isOpen()):
            self.message_string = 'Device connected'
            self.connected = 2
            return 0

    def on_connected(self, instance, value):
        if (value == 0):
            self.is_streaming = False
            self.message_string = 'Device disconnected'
        
    def start_streaming(self):
        if (not (self.connected == 2)):
            self.message_string = 'Board is not connected.'
            return
        
        if (not (self.is_streaming)):
            self.message_string = 'Started streaming'
            self.port.write('b'.encode('utf-8'))
            self.is_streaming = True
            self.read_state = 0
            read_thread = threading.Thread(target=self.collect_data)
            read_thread.daemon = True
            read_thread.start()
            self.samples_counter = 0

    def collect_data(self):
        print("Started collect data thread")
        while(self.is_streaming):
            self.read_serial_binary()

    def read_serial_binary(self, max_bytes_to_skip=3000):
        '''
        Parses incoming data packet into a Sample
        Incoming packet structure:
        START_BYTE(1)| DATA_MSB(1) | DATA_LSB(1) | END_BYTE (1)
        '''
        def read(n):
            bb = self.port.read(n)
            if not bb:
                self.connected = 0
            else:
                return bb
        for rep in range(max_bytes_to_skip):
            # ---------Start Byte ---------
            if self.read_state == 0:
                b = read(1)
                if (b == -999):
                    break
                if struct.unpack('B', b)[0] == 0xA0:
                    self.read_state = 1
                    if (rep != 0):
                        print (f"Skipped {rep} bytes before start")
                        rep = 0
            # ---------DATA MSB and LSB---------
            elif self.read_state == 1:
                # Read 2 bytes for each
                b = read(2)
                unpack = struct.unpack('2B', b)
                sensor_data = (((unpack[0] << 8) & 0xFFFF) | unpack[1])
                sensor_data = sensor_data/65535*5
                self.read_state = 2
            # ---------End Byte---------
            elif self.read_state == 2:
                b = read(1)
                if struct.unpack('B', b)[0] == 0xC0:
                    self.read_state = 0
                    self.samples_counter += 1
                    for callback in self.callbacks:
                        callback(sensor_data)
                    return sensor_data

    def stop_streaming(self):
        self.message_string = 'Stopped streaming data'
        self.is_streaming = False
        self.port.write('s'.encode('utf-8'))

    def select_wave(self, wave):
        if (wave.upper() == 'SINE'):
            self.port.write('e'.encode('utf-8'))
        elif (wave.upper() == 'TRIANGLE'):
            self.port.write('f'.encode('utf-8'))

    def select_range(self, range_val):
        if (range_val.upper() == 'SMALL'):
            self.port.write('t'.encode('utf-8'))
        elif (range_val.upper() == 'LARGE'):
            self.port.write('y'.encode('utf-8'))
    
    def is_connected(self):
        if (self.connected == 2):
            return True
        else:
            return False