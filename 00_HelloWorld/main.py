##
#   @brief          Simple Kivy App.
#
#   This a Kivy app that only shows a Label in your screen.
#
from kivy.app import App
from kivy.uix.label import Label

##
#   @brief          FirstApp class.
#
#    The FirstApp is a simple app containing
#    only one widget, a label, showing a string.
#    No additional interaction is provided.


class FirstApp(App):

    def build(self):
        """
        Return the root widget of the app.
        """
        return Label(text="Hello, World")


FirstApp().run()
