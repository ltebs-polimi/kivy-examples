##
#   @brief          Simple Kivy App showing layout functionality.
#
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty

##
#   @brief          Root widget of the App.
#
#   The container is a BoxLayout that acts as a root widget
#   of the App, containing inside all the other widgets.
#


class Container(BoxLayout):

    connection_label = ObjectProperty(None)
    connection_button = ObjectProperty(None)

    ##
    #   @brief          Initialization function.
    def __init__(self, **kwargs):
        self.connected = False
        super(Container, self).__init__(**kwargs)

    ##
    #   @brief          Callback called on button press.
    #
    #   Update button and label text, update state.
    def button_pressed_callback(self):
        if (self.connected):
            self.connection_button.text = 'Connect'
            self.connection_label.text = 'Disconnected'
            self.connected = False
        else:
            self.connection_button.text = 'Disconnect'
            self.connection_label.text = 'Connected'
            self.connected = True
##
#   @brief          PropertyApp class.
#
#   The PropertyApp is a simple app used to show object properties
#   and references in Kivy.


class PropertyApp(App):
    def build(self):
        return Container()


PropertyApp().run()
