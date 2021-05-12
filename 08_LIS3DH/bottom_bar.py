from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
import communication

##
#   @brief          Bottom bar widget used to display debug messages.
#   
#   The bottom bar widget receives updates from several widgets in
#   form of a simple string that is displayed. Furthermore, the current
#   connection status is displayed in the form of a colored label.
class BottomBar(BoxLayout):

    ##
    #   @brief          Reference to label displaying debug messages.
    message_label = ObjectProperty(None)

    ##
    #   @brief          Reference to label displaying connection status.
    connection_label = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(BottomBar, self).__init__(**kwargs)

    ##
    #   @brief          Update current text and display new received string.
    #
    #   @param[in]      instance: the object updating text.
    #   @param[in]      value: the new string to be shown.
    def update_text(self, instance, value):
        self.message_label.text = value

    ##
    #   @brief          Callback called upon change in connection state.
    #
    #   Update connection label based on new connection state.
    #
    #   @param[in]      instance: the object updating the connection state.
    #   @param[in]      value: the new connection state.
    def connection_event(self, instance, value):
        if (value == communication.CONNECTION_STATE_FOUND):
            self.connection_label.update_color(1, 1, 0)
            self.connection_label.color = (0, 0, 0, 1)
        elif (value == communication.CONNECTION_STATE_CONNECTED):
            self.connection_label.update_color(0, 0.5, 0)
            self.connection_label.color = (1, 1, 1, 1)
        else:
            self.connection_label.update_color(0.3, 0.3, 0.3, 1.0)
            self.connection_label.color = (1, 1, 1, 1)
        
##
#   @brief          Label with colored background.
#   
#   This is a label that allows to update the background color.
class ColoredLabel(Label):

    ##
    #   @brief          Update background color of the label.
    #
    #   @param[in]      r: red color.
    #   @param[in]      g: green color.
    #   @param[in]      b: blu color.
    def update_color(self, r, g, b):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(r,g,b,1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect,
                    size=self.update_rect)
    
    ##
    #   @brief          Update rectangle of the label.
    #
    #   This is required so that, when resizing the window, the
    #   color of the label continues to fill the background.
    #
    def update_rect(self, *kwargs):
        self.rect.pos = self.pos
        self.rect.size = self.size