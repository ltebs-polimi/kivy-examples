##
#   @brief          Simple Kivy App showing layout functionality.
#
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout

##
#   @brief          Root widget of the App.
#
#   The container is a BoxLayout that acts as a root widget
#   of the App, containing inside all the other widgets.
#


class Container(BoxLayout):
    pass

##
#   @brief          LAdvancedApp class.
#
#   The LAdvancedApp is a simple app used to show layout functionality
#   in Kivy.


class LAdvancedApp(App):
    def build(self):
        return Container()


LAdvancedApp().run()
