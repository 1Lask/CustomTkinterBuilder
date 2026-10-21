from customtkinter import CTkLabel, CTkImage
from PIL import Image
from PackArgs import PackArgs
from widgets import BaseWidgetClass
class Label(CTkLabel, PackArgs, BaseWidgetClass):
    def __init__(self, *args, properties, **kwargs):
        super(Label, self).__init__(*args, **kwargs)
        BaseWidgetClass.__init__(self)
        self.type = "LABEL"
        self.properties = properties
        self.image = None
        self.img = None
        self.size = None
        self.pack_options = {}
        self.order = 0
        self.pack_propagate(False)
        self.num = 0
        self.name = None
        self.family = self.cget("font").cget("family")
        self.configure(bg_color="transparent")
        self.props = {}
        self.bind_mouse(properties)

    def __repr__(self):
        return f"{self.type}_{str(self.order)}"

    def get_name(self):
        return self.name.replace(" ", "_")

    def get_class(self):
        return "CTkLabel"

    def save(self, func, key, val, arg):

        if key == "font_family":
            self.family = val
        self.props[key] = val
        func(arg)

    def get_not_transparent_color(self, widget):
        try:
            c = widget.get_class()
            if widget.master.cget("fg_color") != "transparent":
                return widget.master.cget("fg_color")
            else:
                return self.get_not_transparent_color(widget.master)
        except Exception as e:
            return self.get_not_transparent_color(widget.master)

    def configure(self, require_redraw=False, **kwargs):
        if "bg_color" in kwargs:
            if kwargs["bg_color"] == "transparent":
                kwargs["bg_color"] = self.get_not_transparent_color(self)

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
        self.properties.add_option(self.properties.GEOMETRY_CONTENT, "ID", "SINGLELINE_TEXT", "id", {"val": self.name, "callback": lambda val: (self.properties.main.hierarchy.update_text(self.name, val), self.change_name(val))})

        self.properties.add_option(self.properties.GEOMETRY_CONTENT, "Width", "SPINBOX", "Width", {"to": 500, "from": 0, "val": int(self.cget("width")), "callback": lambda val: self.save(lambda val: self.configure(width=val), "width", int(val), int(val))})
        self.properties.add_option(self.properties.GEOMETRY_CONTENT, "Height", "SPINBOX", "Height", {"to": 500, "from": 0, "val": int(self.cget("height")), "callback": lambda val: self.save(lambda val: self.configure(height=val), "height", int(val), int(val))})
        self.properties.add_option(self.properties.GEOMETRY_CONTENT, "Text", "TEXT", "text", {"val": self.cget("text"), "callback": lambda val: self.save(lambda val: self.configure(text=val), "text", val, val)})
        self.properties.add_option(self.properties.GEOMETRY_CONTENT, "Image", "IMAGE", "image", {"image": self.image, "size": self.get_size, "key": "image", "callback": self.set_image})

        # Had to reset the image for compound option to take effect
        self.properties.add_option(self.properties.ARRANGEMENT, "Compound", "COMBO", "compound", {"vals": ["top", "bottom", "left", "right"], "default": self.cget("compound"), "callback": lambda val: self.save(lambda val: (self.configure(compound=val, image=None), self.set_compound(self.image)), "compound", val, val)})
        self.properties.add_option(self.properties.ARRANGEMENT, "Anchor", "COMBO", "anchor", {"vals": ["n", "ne", "e", "se", "s", "sw", "w", "nw", "center"], "default": self.cget("anchor"), "callback": lambda val: self.save(lambda val: self.configure(anchor=val), "anchor", val, val)})
        self.properties.add_option(self.properties.ARRANGEMENT, "Justify", "COMBO", "justify", {"vals": ["left", "right", "center"], "default": self.cget("justify"), "callback": lambda val: self.save(lambda val: self.configure(justify=val), "justify", val, val)})
        self.properties.add_option(self.properties.ARRANGEMENT, "Padx", "SPINBOX", "PADX", {"to": 500, "from": 0, "val": int(self.cget("padx")), "callback": lambda val: self.save(lambda val: self.configure(padx=val), "padx", int(val), int(val))})
        self.properties.add_option(self.properties.ARRANGEMENT, "Pady", "SPINBOX", "PADY", {"to": 500, "from": 0, "val": int(self.cget("pady")), "callback": lambda val: self.save(lambda val: self.configure(pady=val), "pady", int(val), int(val))})
        self.properties.add_option(self.properties.GEOMETRY_CONTENT, "Corner Radius", "SPINBOX", "Corner Radius", {"to": 100, "from": 0, "val": self.cget("corner_radius"), "callback": lambda val: self.save(lambda val: self.configure(corner_radius=val), "corner_radius", int(val), int(val))})
        self.properties.add_option(self.properties.GEOMETRY_CONTENT, "Wrap Length", "SPINBOX", "wraplength", {"to": 100, "from": 0, "val": self.cget("wraplength"), "callback": lambda val: self.save(lambda val: self.configure(wraplength=val), "wraplength", int(val), int(val))})

        #print("Properties", self.family)
        self.properties.add_option(self.properties.STYLES, "Font Family", "FONT_FAMILY", "font_family", {"key": "font_family", "default": self.family, "callback": lambda val: self.save(lambda val: self.cget("font").configure(family=val), "font_family", val, val)})
        self.properties.add_option(self.properties.STYLES, "Font Size", "SPINBOX", "font_size", {"to": 500, "from": -500, "val": self.cget("font").cget("size"), "callback": lambda val: self.save(lambda val: self.cget("font").configure(size=int(val)), "font_size", int(val), int(val))})
        self.properties.add_option(self.properties.STYLES, "Font Weight", "COMBO", "font_weight", {"vals": ["bold", "normal"], "default": self.cget("font").cget("weight"), "callback": lambda val: self.save(lambda val: self.cget("font").configure(weight=val), "font_weight", val, val)})
        self.properties.add_option(self.properties.STYLES, "Font Slant", "COMBO", "font_slant", {"vals": ["italic", "roman"], "default": self.cget("font").cget("slant"), "callback": lambda val: self.save(lambda val: self.cget("font").configure(slant=val), "font_slant", val, val)})
        self.properties.add_option(self.properties.STYLES, "Font Underline", "COMBO", "font_underline", {"vals": ["True", "False"], "default": str(bool(self.cget("font").cget("underline"))), "callback": lambda val: self.save(lambda val: self.cget("font").configure(underline=val), "font_underline", self._bool_change(val), self._bool_change(val))})
        self.properties.add_option(self.properties.STYLES, "Font Overstrike", "COMBO", "font_overstrike", {"vals": ["True", "False"], "default": str(bool(self.cget("font").cget("overstrike"))), "callback": lambda val: self.save(lambda val: self.cget("font").configure(overstrike=val), "font_overstrike", self._bool_change(val), self._bool_change(val))})

        self.properties.add_option(self.properties.STYLES, "FG Color", "COLOR_COMBO", "fg_color", {"color": self.cget("fg_color"), "key": "fg_color", "transparent": True, "callback": lambda val: self.save(lambda val: self.configure(fg_color=val), "fg_color", val, val)})
        self.properties.add_option(self.properties.STYLES, "BG Color", "COLOR_COMBO", "bg_color", {"color": self.cget("bg_color"), "key": "bg_color", "transparent": True, "callback": lambda val: self.save(lambda val: self.configure(bg_color=val), "bg_color", val, val)})
        self.properties.add_option(self.properties.STYLES, "Text Color", "COLOR_COMBO", "text_color", {"color": self.cget("text_color"), "key": "text_color", "transparent": False, "callback": lambda val: self.save(lambda val: self.configure(text_color=val), "text_color", val, val)})
        self.default()

    def get_size(self):
        return self.size

    def set_image(self, img, size):
        if img != "":
            self.image = img
            img = Image.open(img)
            img = CTkImage(light_image=img, dark_image=img, size=size)

            self.configure(image=img, width=int(self.cget("width"))+1)
            self.configure(width=int(self.cget("width"))-1)
            self.img = img
            self.size = size
            self.props["image"] = img
        else:
            self.image = None
            with_img_width = self.winfo_width()
            with_img_height = self.winfo_height()
            real_width = self.cget("width")
            real_height = self.cget("height")
            self.configure(image="", width=with_img_width, height=with_img_height)
            self.update()
            self.configure(width=real_width, height=real_height)
            self.props.pop("image")

        self.update()
        self.properties.main.draw_box(self.properties.main.hierarchy.widget)
    def set_compound(self, image):
        self.set_image(image, self.size)
