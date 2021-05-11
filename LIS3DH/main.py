#!/usr/bin/python3

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.properties import ObjectProperty  #pylint: disable=no-name-in-module
from communication import KivySerial

# Load all required kv files
Builder.load_file('toolbar.kv')
Builder.load_file('bottom_bar.kv')
Builder.load_file('dialogs.kv')
Builder.load_file('graph_tabs.kv')

class ContainerLayout(BoxLayout):
    """
    @brief Root widget of the PSoC-Kivy app.
    """

    """
    @brief Lateral toolbar widget.
    """
    toolbar = ObjectProperty(None)

    """
    @brief Bottom bar widget.
    """ 
    bottom_bar = ObjectProperty(None)

    """
    @brief Graph widget.
    """
    graph_w = ObjectProperty(None)

    streaming_button = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        """
        @brief Initialize class.
        """
        self.serial = KivySerial()
        super(ContainerLayout, self).__init__(**kwargs)

    def on_toolbar(self, instance, value):
        """
        @brief Callback for toolbar widget.
        """
        try:
            self.toolbar.bind(message_string=self.bottom_bar.update_text)
        except:
            pass

    def on_bottom_bar(self, instance, value):
        """
        @brief Callback for bottom bar widget.

        Bind several properties when bottom bar is created.
        """
        try:
            self.toolbar.bind(message_string=self.bottom_bar.update_text)
            self.serial.bind(message_string=self.bottom_bar.update_text)
            self.serial.bind(connected=self.bottom_bar.connection_event)
            self.serial.bind(connected=self.connection_event)
        except:
            raise

    def on_graph_w(self, instance, value):
        """
        @brief Callback for graph widget.
        """
        self.serial.add_callback(self.graph_w.update_plot)

    def connection_event(self, instance, value):
        """
        @brief Callback for connection event.

        Enable/Disable widget based on connection status.
        """
        if (self.serial.is_connected()):
            self.streaming_button.disabled = False
            self.toolbar.disabled = False
        else:
            self.streaming_button.disabled = True
            self.toolbar.disabled = True

    def streaming(self):
        """
        @brief Start streaming from the serial port.
        """
        if (not self.serial.is_streaming):
            self.serial.start_streaming()
            self.streaming_button.text = 'Stop'
        else:
            self.serial.stop_streaming()
            self.streaming_button.text = 'Start'

class LIS3DHApp(App):
    def build(self):
        return ContainerLayout()

if __name__ == '__main__':
    LIS3DHApp().run()    
