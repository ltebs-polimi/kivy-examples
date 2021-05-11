from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from communication import KivySerial
from random import randint
from kivy.config import Config

Config.set('kivy', 'desktop', 1)
Config.set('input', 'mouse', 'mouse,disable_multitouch')

Builder.load_file('toolbar.kv')
Builder.load_file('bottom_bar.kv')
Builder.load_file('dialogs.kv')
Builder.load_file('graph_tabs.kv')

class ContainerLayout(BoxLayout):
    
    toolbar = ObjectProperty(None)
    bottom_bar = ObjectProperty(None)
    graph_w = ObjectProperty(None)

    def __init__(self, **kwargs):
        self.serial = KivySerial()
        super(ContainerLayout, self).__init__(**kwargs)
    
    def on_toolbar(self, instance, value):
        try:
            self.toolbar.bind(message_string=self.bottom_bar.update_text)
        except:
            pass
    
    def on_bottom_bar(self, instance, value):
        try:
            self.toolbar.bind(message_string=self.bottom_bar.update_text)
            self.serial.bind(message_string=self.bottom_bar.update_text)
            self.serial.bind(connected=self.bottom_bar.connection_event)
            self.serial.bind(connected=self.connection_event)
        except:
            pass
        
    def on_graph_w(self, instance, value):
        self.serial.add_callback(self.graph_w.update_plot)
        
    def connection_event(self, instance, value):
        if (self.serial.is_connected()):
            self.start_streaming_button.disabled = False
            self.stop_streaming_button.disabled = False
        else:
            self.start_streaming_button.disabled = False
            self.stop_streaming_button.disabled = False

    def start_streaming(self):
        self.serial.start_streaming()

    def stop_streaming(self):
        self.serial.stop_streaming()

class PSoCKivy(App):
    def build(self):
        return ContainerLayout()

PSoCKivy().run()