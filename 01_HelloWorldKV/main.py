##
#   @brief          Simple Kivy App.
#
#   This a Kivy app that only shows a Label in your screen.
#
from kivy.app import App
from kivy.uix.widget import Widget

##
#   @brief          AppWidget class.
#
#   This widget is the root widget of the App. The current
#   implementation implements a simple Label.


class AppWidget(Widget):
    pass

##
#   @brief          FirstApp class.
#
#   The FirstApp is a simple app containing
#   only one widget, a \ref App Widget, showing a string.
#   No additional interaction is provided.


class FirstApp(App):

    def build(self):
        """
        Return the root widget of the app.
        """
        return AppWidget()


FirstApp().run()
