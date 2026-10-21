from customtkinter import CTkFrame, CTkImage
from PIL import Image
from widgets import BaseWidgetClass
class Main(CTkFrame, BaseWidgetClass):
    def __init__(self, *args, properties, **kwargs):
        super().__init__(*args, **kwargs)
        BaseWidgetClass.__init__(self)
        self.type = "MAIN"
        self.properties = properties
        self.image = None
        self.img = None
        self.size = None
        self.pack_options = {}
        self.pack_propagate(False)
        self.order = 0
        self.num = None
        self.name = None

        self.props = {}

    def __repr__(self):

        return f"{self.type}_{str(self.order)}"

    def _set_appearance_mode(self, mode_string):
        bg_color = ("grey10", "grey80")
        self.configure(bg_color=bg_color[self.properties.main.appearance.get()])
        super()._set_appearance_mode(mode_string)

    def get_class(self):
        return "CTk"

    def get_name(self):
        return self.name.replace(" ", "_")

    def save(self, func, key, val, arg):
        self.props[key] = val
        func(arg)
        if key in ["width", "height"]:
            main = self.properties.main
            main_window_panel = main.r.master.master
            main_window = main.r
            visible_area = main_window_panel.winfo_height()
            content_height = main_window.cget("height")
            hidden_area = (content_height - visible_area)
            offset = hidden_area // 2
            offset += 50

            main.vert_max_offset = abs(offset)

            visible_area = main_window_panel.winfo_width()
            content_height = main_window.cget("width")
            hidden_area = (content_height - visible_area)
            offset = hidden_area // 2
            offset += 50

            main.horiz_max_offset = abs(offset)

            main.horiz_scrl.set(0)
            main.vert_scrl.set(0)
            main_window.place(x=0, y=0)

    def configure(self, require_redraw=False, **kwargs):
        super().configure(require_redraw, **kwargs)


    def _bool_change(self, val):
        if val == "True":
            return True
        elif val == "False":
            return False

    def change_name(self, name):
        self.name = name

    def on_drag_start(self, event):
        self.properties.destroy_children()
        self.properties.add_option(self.properties.GEOMETRY_CONTENT, "Width", "SPINBOX", "Width", {"to": 500, "from": 0, "val": int(self.cget("width")), "callback": lambda val: self.save(lambda val: self.configure(width=val), "width", int(val), int(val))})
        self.properties.add_option(self.properties.GEOMETRY_CONTENT, "Height", "SPINBOX", "Height", {"to": 500, "from": 0, "val": int(self.cget("height")), "callback": lambda val: self.save(lambda val: self.configure(height=val), "height", int(val), int(val))})
        self.properties.add_option(self.properties.GEOMETRY_CONTENT, "Title", "TEXT", "title", {"val": self.properties.main.title, "callback": lambda val: self.save(lambda val: self.properties.main.change(title=val), "title", val, val)})
        self.properties.add_option(self.properties.STYLES, "FG Color", "COLOR_COMBO", "fg_color", {"color": self.cget("fg_color"), "key": "fg_color", "transparent": True, "callback": lambda val: self.save(lambda val: self.configure(fg_color=val), "fg_color", val, val)})
