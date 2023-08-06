from ipywidgets import *
from IPython.display import clear_output, display
from tkinter import Tk, filedialog
from traitlets import traitlets

class selectfiles(widgets.Button):
    def __init__(self, files=None, *args, **kwargs):
        super(selectfiles, self).__init__(*args, **kwargs)
        # Create the value attribute.
        self.description = "File Select"
        self.add_traits(files=traitlets.Any(files))
        self.on_click(self.select_files)
        display(self)
    
    def select_files(self, b):
        clear_output()
        root = Tk()
        root.withdraw()
        root.call('wm', 'attributes', '.', '-topmost', True)
        b.files = filedialog.askopenfilename(multiple=True)