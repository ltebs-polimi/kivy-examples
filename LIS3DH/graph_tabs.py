from datetime import datetime

from kivy.lang import Builder
from kivy.uix.textinput import TextInput
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.properties import BooleanProperty, ObjectProperty, NumericProperty #pylint:disable=no-name-in-module
import re
from kivy.garden.graph import MeshLinePlot, LinePlot #pylint:disable=no-name-in-module, import-error
from kivy.graphics import Color, Rectangle

class GraphTabs(TabbedPanel):
    """
    @brief Main tabbed panel to show tabbed items.
    """

    """
    @brief Wav dac plot tabbed panel.
    """
    acc_tab = ObjectProperty(None)
    def __init__(self, **kwargs):
        super(GraphTabs, self).__init__(**kwargs)

    def update_plot(self, packet):
        """
        @brief Function called to update the plots in the tabbed panel.
        """
        self.acc_tab.update_plot(packet)

class LIS3DHTabbedPanelItem(TabbedPanelItem):
    """
    @brief Item for a tabbed panel in which a graph is shown.
    """

    """
    @brief Graph widget.
    """
    graph = ObjectProperty(None)

    """
    @brief Plot settings widget.
    """
    plot_settings = ObjectProperty(None)

    """
    @brief Refresh rate: ~ 50 fps (100 Hz/2)
    """
    n_points_per_update = NumericProperty(1)

    def __init__(self, **kwargs):
        super(LIS3DHTabbedPanelItem, self).__init__(**kwargs)
        self.n_seconds = 20          # Initial number of samples to be shown
        self.x_axis_n_points_collected = [] # Number of new collected points
        self.y_axis_n_points_collected = [] # Number of new collected points
        self.z_axis_n_points_collected = [] # Number of new collected points
        self.sample_rate = 1       # Sample rate for data streaming

    def on_graph(self, instance, value):
        """
        @brief Callback called when graph widget is ready.
        """
        self.graph.xmin = -self.n_seconds
        self.graph.xmax = 0
        self.graph.xlabel = 'Time (s)'
        self.graph.x_ticks_minor = 1
        self.graph.x_ticks_major = 5
        self.graph.y_ticks_minor = 1
        self.graph.y_ticks_major = 1
        self.graph.x_grid_label = True
        self.graph.ymin = -2
        self.graph.ymax = 2
        self.graph.y_grid_label = True
        # Compute number of points to show
        self.n_points = self.n_seconds * self.sample_rate  # Number of points to plot
        # Compute time between points on x-axis
        self.time_between_points = (self.n_seconds)/float(self.n_points)
        # Initialize x and y points list
        self.x_points = [x for x in range(-self.n_points, 0)]
        for j in range(self.n_points):
            self.x_points[j] = -self.n_seconds + (j+1) * self.time_between_points
        self.x_axis_points = [0 for y in range(-self.n_points, 0)]
        self.y_axis_points = [0 for y in range(-self.n_points, 0)]
        self.z_axis_points = [0 for y in range(-self.n_points, 0)]  

        self.x_plot = LinePlot(color=(0.75, 0.4, 0.4, 1.0))
        self.x_plot.line_width = 2
        self.x_plot.points = zip(self.x_points, self.x_axis_points)

        self.y_plot = LinePlot(color=(0.4, 0.4, 0.75, 1.0))
        self.y_plot.line_width = 2
        self.y_plot.points = zip(self.x_points, self.y_axis_points)

        self.z_plot = LinePlot(color=(0.4, 0.75, 0.4, 1.0))
        self.z_plot.line_width = 2
        self.z_plot.points = zip(self.x_points, self.z_axis_points)

        self.graph.add_plot(self.x_plot)
        self.graph.add_plot(self.y_plot)
        self.graph.add_plot(self.z_plot)

    def on_plot_settings(self, instance, value):
        """
        @brief Callback called when plot_settings widget is ready.

        Bint several properties together.
        """
        self.plot_settings.bind(n_seconds=self.graph.setter('xmin'))
        self.plot_settings.bind(ymin=self.graph.setter('ymin'))
        self.plot_settings.bind(ymax=self.graph.setter('ymax'))

    def update_plot(self, packet):
        """
        @brief Update plot based on value and refresh rate.
        """
        self.x_axis_n_points_collected.append(packet.get_x_data())
        self.y_axis_n_points_collected.append(packet.get_y_data())
        self.z_axis_n_points_collected.append(packet.get_z_data())
        if (len(self.x_axis_n_points_collected) == self.n_points_per_update):
            for idx in range(self.n_points_per_update):
                self.x_axis_points.append(self.x_axis_points.pop(0))
                self.x_axis_points[-1] = self.x_axis_n_points_collected[idx]
                self.y_axis_points.append(self.y_axis_points.pop(0))
                self.y_axis_points[-1] = self.y_axis_n_points_collected[idx]
                self.z_axis_points.append(self.z_axis_points.pop(0))
                self.z_axis_points[-1] = self.z_axis_n_points_collected[idx]
            self.x_plot.points = zip(self.x_points, self.x_axis_points)
            self.y_plot.points = zip(self.x_points, self.y_axis_points)
            self.z_plot.points = zip(self.x_points, self.z_axis_points)
            self.x_axis_n_points_collected = []
            self.y_axis_n_points_collected = []
            self.z_axis_n_points_collected = []

class PlotSettings(BoxLayout):
    """
    @brief Class to show some settings related to the plot.
    """

    """
    @brief Number of seconds to show on the plot.
    """
    seconds_spinner = ObjectProperty(None)
    
    """
    @brief Minimum value for y axis text input widget.
    """
    ymin_input = ObjectProperty(None)

    """
    @brief Maximum value for y axis text input widget.
    """
    ymax_input = ObjectProperty(None)

    """
    @brief Current number of seconds shown.
    """
    n_seconds = NumericProperty(0)

    """
    @brief Numeric value of ymin axis minimum value.
    """
    ymin = NumericProperty(0)

    """
    @brief Numeric value of ymin axis maximum value.
    """
    ymax = NumericProperty(5)

    def __init__(self, **kwargs):
        super(PlotSettings, self).__init__(**kwargs)
        self.n_seconds = 20

    def on_seconds_spinner(self, instance, value):
        """
        @brief Bind change on seconds spinner to callback.
        """
        self.seconds_spinner.bind(text=self.spinner_updated)

    def on_ymin_input(self, instance, value):
        """
        @brief Bind enter pressed on ymin text input to callback.
        """
        self.ymin_input.bind(enter_pressed=self.axis_changed)

    def on_ymax_input(self, instance, value):
        """
        @brief Bind enter pressed on on ymax text input to callback.
        """
        self.ymax_input.bind(enter_pressed=self.axis_changed)

    def spinner_updated(self, instance, value):
        """
        @brief Get new value of seconds to show on the plot.
        """
        self.n_seconds = -int(self.seconds_spinner.text)

    def axis_changed(self, instance, focused):
        """
        @brief Called when a new value of ymin or ymax is entered on the GUI.
        """
        if (not focused):
            if (not ((self.ymin_input.text == '') or (self.ymax_input.text == ''))):
                y_min = float(self.ymin_input.text)
                y_max = float(self.ymax_input.text)
                if (y_min >= y_max):
                    self.ymin_input.text = f"{self.ymin:.2f}"
                    self.ymax_input.text = f"{self.ymax:.2f}"
                else:
                    self.ymin = y_min
                    self.ymax = y_max
            elif (self.ymin_input.text == ''):
                self.ymin_input.text = f"{self.ymin:.2f}"
            elif (self.ymax_input.text == ''):
                self.ymax_input.text = f"{self.ymax:.2f}"


class FloatInput(TextInput):
    pat = re.compile('[^0-9]')
    enter_pressed = BooleanProperty(None)
    
    def __init__(self, **kwargs):
        super(FloatInput, self).__init__(**kwargs)
        self.bind(focus=self.on_focus) #pylint:disable=no-member
        self.multiline = False

    def insert_text(self, substring, from_undo=False):
        pat = self.pat
        if ( (len(self.text) == 0) and substring == '-'):
            s = '-'
        else:
            if '.' in self.text:
                s = re.sub(pat, '', substring)
            else:
                s = '.'.join([re.sub(pat, '', s) for s in substring.split('.', 1)])
        return super(FloatInput, self).insert_text(s, from_undo=from_undo)
    
    def on_focus(self, instance, value):
        self.enter_pressed = value