from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from serial.serialutil import SerialException
from serial.serialwin32 import Serial
from serial.tools.list_ports import comports
import serial
##
#   @brief          Root widget of the App.
#
#   The container is a BoxLayout that acts as a root widget
#   of the App, containing inside all the other widgets.
#


class Container(BoxLayout):

    connection_button = ObjectProperty(None)
    com_ports_spinner = ObjectProperty(None)

    def __init__(self, **kwargs):
        self.connected = False
        super(Container, self).__init__(*kwargs)
        

    def on_com_ports_spinner(self, instance, value):
        ports = [port.device for port in comports()]
        self.com_ports_spinner.values = ports
        if len(ports) > 0:
            self.com_ports_spinner.text = ports[0]
        else:
            self.com_ports_spinner.text = 'No COM port found'
            self.com_ports_spinner.disabled = True
        
    def button_pressed_callback(self):
        if (len(self.com_ports_spinner.values) == 0):
            print('No COM port selected')
            return
        #if len(self.com_ports_spinner.values)
        if (not self.connected):
            try:
                self.ser = serial.Serial(
                    port=self.com_ports_spinner.text, baudrate=115200)
                if (self.ser.is_open):
                    print("Connection successful")
                    self.connected = True
                    self.connection_button.text = 'Disconnect'
                    self.com_ports_spinner.disabled = True
            except SerialException:
                print("Could not connect to serial port")
        else:
            self.ser.close()
            print("Disconnection successful")
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
