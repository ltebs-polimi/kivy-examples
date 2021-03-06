from kivy.lang import Builder
from kivy.uix.textinput import TextInput
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.properties import BooleanProperty, ObjectProperty, NumericProperty
import re
from kivy.garden.graph import LinePlot
from kivy.graphics import Color, Rectangle

class GraphTabs(TabbedPanel):
    wave_dac_tab = ObjectProperty(None)
    def __init__(self, **kwargs):
        super(GraphTabs, self).__init__(**kwargs)
    
    def update_plot(self, value):
        self.wave_dac_tab.update_plot(value)

class GraphPanelItem(TabbedPanelItem):
    graph = ObjectProperty(None)
    plot_settings = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(GraphPanelItem, self).__init__(**kwargs)
        self.n_seconds = 60
        self.n_points_per_update = 10
        self.n_points_collected = []

    def on_graph(self, instance, value):
        self.graph.xmin = -self.n_seconds
        self.graph.xmax = 0
        self.graph.xlabel = 'Time (s)'
        self.graph.x_ticks_minor = 1
        self.graph.x_ticks_major = 5
        self.graph.y_ticks_minor = 1
        self.graph.y_ticks_major = 1
        self.graph.x_grid_label = True
        self.graph.ymin = 0
        self.graph.ymax = 5
        self.graph.y_grid_label = True
        self.sample_rate = 100
        self.n_points = self.n_seconds * 100  # Number of points to plot
        self.time_between_points = (self.n_seconds)/float(self.n_points)
        self.x_points = [x for x in range(-self.n_points, 0)]
        for j in range(self.n_points):
            self.x_points[j] = -self.n_seconds + j * self.time_between_points
        self.y_points = [0 for y in range(-self.n_points, 0)]
        
    def on_plot_settings(self, instance, value):
        self.plot_settings.bind(n_seconds=self.graph.setter('xmin'))
        self.plot_settings.bind(ymin=self.graph.setter('ymin'))
        self.plot_settings.bind(ymax=self.graph.setter('ymax'))
    
    def update_plot(self, value):
        self.n_points_collected.append(value)
        if (len(self.n_points_collected) == self.n_points_per_update):
            for val in self.n_points_collected:
                self.y_points.append(self.y_points.pop(0))
                self.y_points[-1] = val
            self.plot.points = zip(self.x_points, self.y_points)
            self.n_points_collected = []

class WaveDACPlot(GraphPanelItem):
    def on_graph(self, instance, value):
        super(WaveDACPlot, self).on_graph(instance, value)
        self.graph.ylabel = 'Amplitude (V)'
        self.plot = LinePlot(color=(0.5, 0.4, 0.4, 1.0))
        self.plot.line_width = 1.5
        self.plot.points = zip(self.x_points, self.y_points)
        self.graph.add_plot(self.plot)

class PlotSettings(BoxLayout):
    seconds_spinner = ObjectProperty(None)
    ymin_input = ObjectProperty(None)
    ymax_input = ObjectProperty(None)
    legend = ObjectProperty(None)
    n_seconds = NumericProperty(0)
    ymin = NumericProperty(0)
    ymax = NumericProperty(5)
    
    def __init__(self, **kwargs):
        super(PlotSettings, self).__init__(**kwargs)
        self.n_seconds = 60

    def on_seconds_spinner(self, instance, value):
        self.seconds_spinner.bind(text=self.spinner_updated)
    
    def on_ymin_input(self, instance, value):
        self.ymin_input.bind(enter_pressed=self.axis_changed)
    
    def on_ymax_input(self, instance, value):
        self.ymax_input.bind(enter_pressed=self.axis_changed)
    
    def spinner_updated(self, instance, value):
        self.n_seconds = -int(self.seconds_spinner.text)

    def axis_changed(self, instance, focused):
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
        self.bind(focus=self.on_focus)
        self.multiline = False

    def insert_text(self, substring, from_undo=False):
        pat = self.pat
        
        if '.' in self.text:
            s = re.sub(pat, '', substring)
        else:
            s = '.'.join([re.sub(pat, '', s) for s in substring.split('.', 1)])
        
        return super(FloatInput, self).insert_text(s, from_undo=from_undo)
    
    def on_focus(self, instance, value):
        self.enter_pressed = value