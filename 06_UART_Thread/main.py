from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
import serial
from serial.serialutil import SerialException
from serial.tools.list_ports import comports
import threading

##
#   @brief          Root widget of the App.
#
#   The container is a BoxLayout that acts as a root widget
#   of the App, containing inside all the other widgets.
#


class Container(BoxLayout):

    connection_button = ObjectProperty(None)
    com_ports_spinner = ObjectProperty(None)
    debug_label = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(Container, self).__init__(*kwargs)
        self.connected = False

    def on_com_ports_spinner(self, instance, value):
        ports = [port.device for port in comports()]
        self.com_ports_spinner.values = ports
        self.com_ports_spinner.text = ports[0]

    def button_pressed_callback(self):
        connection_thread = threading.Thread(target=self.connect_to_port)
        connection_thread.daemon = True
        connection_thread.start()
        self.debug_label.text = 'Thread started'
    
    def connect_to_port(self):
        if (not self.connected):
            try:
                self.connection_button.disabled = True
                self.com_ports_spinner.disabled = True
                self.ser = serial.Serial(
                    port=self.com_ports_spinner.text, baudrate=115200)
                if (self.ser.is_open):
                    self.debug_label.text = "Connection successful"
                    self.connected = True
                    self.connection_button.text = 'Disconnect'
                    self.com_ports_spinner.disabled = True
            except SerialException:
                self.com_ports_spinner.disabled = False
                self.debug_label.text = "Could not connect to serial port"
            self.connection_button.disabled = False
        else:
            self.ser.close()
            self.debug_label.text = "Disconnection successful"
            self.connected = False
            self.connection_button.text = 'Connect'
            self.com_ports_spinner.disabled = False

##
#   @brief          PropertyApp class.
#
#   The PropertyApp is a simple app used to show object properties
#   and references in Kivy.


class UARTApp(App):
    def build(self):
        return Container()


UARTApp().run()
