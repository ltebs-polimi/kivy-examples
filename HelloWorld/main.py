from kivy.app import App
from kivy.uix.label import Label

class HelloWorldApp(App):
    """
    The HelloWorldApp is a simple app containing
    only one widget, a label, showing a string.
    No additional interaction is provided.
    """
    def build(self):
        """
        Return the root widget of the app.
        """
        return Label(text = "Hello, World")

if __name__ == "__main__":
    # Run the app
    HelloWorldApp().run()