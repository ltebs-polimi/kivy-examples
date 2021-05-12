#!/usr/bin/python3

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.properties import ObjectProperty  # pylint: disable=no-name-in-module
from communication import KivySerial

from kivy.config import Config

# Configure GUI for desktop usage
Config.set('kivy', 'desktop', 1)
Config.set('input', 'mouse', 'mouse,disable_multitouch')
Config.set('kivy', 'exit_on_escape', '0')

# Load all required kv files
Builder.load_file('toolbar.kv')
Builder.load_file('bottom_bar.kv')
Builder.load_file('dialogs.kv')
Builder.load_file('graph_tabs.kv')

##
#   @brief          Root widget of the GUI.
#   
#   The root widget of the GUI contains all the required
#   widgets to achieve proper functionality. It takes care
#   of binding all the properties across widgets.
class ContainerLayout(BoxLayout):

    ##
    #   @brief          Reference to lateral toolbar.
    #
    #   The lateral toolbar contains widgets for interacting
    #   with the GUI and configuring the accelerometer.
    
    toolbar = ObjectProperty(None)

    ##
    #   @brief          Bottom bar widget.
    #
    #   This widget is used to display debug messages on the
    #   GUI.
    
    bottom_bar = ObjectProperty(None)

    ##
    #   @brief          Reference to graph tabbed panel.
    #
    #   The tabbed panel contains widgets which show
    #   acceleration real time plots.

    graph_w = ObjectProperty(None)

    ##
    #   @brief          Reference to streaming button.
    #
    #   Button used to start/stop streaming data from the
    #   accelerometer.

    streaming_button = ObjectProperty(None)

    ##
    #   @brief          Initialization function.
    #
    #   In the init function the serial object is instantied.
    def __init__(self, **kwargs):
        self.serial = KivySerial()
        self.serial.bind(connected=self.connection_event)
        super(ContainerLayout, self).__init__(**kwargs)

    ##
    #   @brief          Callback called when bottom bar widget is displayed on the screen.
    def on_bottom_bar(self, instance, value):
        """
        @brief Callback for bottom bar widget.

        Bind several properties when bottom bar is created.
        """
        self.serial.bind(message_string=self.bottom_bar.update_text)
        self.serial.bind(connected=self.bottom_bar.connection_event)

    ##
    #   @brief          Callback called when graph widget is displayed on the screen.
    #
    #   In this function some properties are bound to the graph widgets so
    #   that it is automatically updated.
    def on_graph_w(self, instance, value):
        self.serial.add_callback(self.graph_w.update_plot)
        self.serial.bind(sample_rate=self.graph_w.update_sample_rate)

    ##
    #   @brief          Callback called when the connection status changes.
    #
    #   Depending on the current connection status of \ref KivySerial, the 
    #   widgets of the GUI are either enabled/disabled.
    def connection_event(self, instance, value):
        if (self.serial.is_connected()):
            self.streaming_button.disabled = False
            self.toolbar.disabled = False
        else:
            self.streaming_button.disabled = True
            self.toolbar.disabled = True

    ##
    #   @brief          Callback called when the streaming button is pressed.
    #
    #   Depending on the current streaming state of the \ref KivySerial, 
    #   streaming is either started or stopped.
    def streaming(self):
        if (not self.serial.is_streaming):
            self.serial.start_streaming()
            self.streaming_button.text = 'Stop'
            self.toolbar.disabled = True
        else:
            self.serial.stop_streaming()
            self.streaming_button.text = 'Start'
            self.toolbar.disabled = False

##
#   @brief          Kivy App main class
class LIS3DHApp(App):
    def build(self):
        return ContainerLayout()


if __name__ == '__main__':
    LIS3DHApp().run()
