from customtkinter import CTkButton, CTkImage
from PIL import Image
from PackArgs import PackArgs
from widgets import BaseWidgetClass


class Button(CTkButton, PackArgs, BaseWidgetClass):
    def __init__(self, *args, properties, **kwargs):
        super().__init__(*args, **kwargs)
        BaseWidgetClass.__init__(self)
        self.type = "BUTTON"
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
        self.bind_mouse(properties)

    def __repr__(self):
        return f"{self.type}_{str(self.order)}"

    def get_class(self):
        return "CTkButton"

    def get_name(self):
        return self.name.replace(" ", "_")

    def save(self, func, key, val, arg):
        self.props[key] = val
        func(arg)

    def configure(self, require_redraw=False, **kwargs):
        super().configure(require_redraw, **kwargs)

    def _bool_change(self, val):
        if val == "True":
            return True
        elif val == "False":
            return False

    def change_name(self, name):
        self.name = name

    def get_size(self):
        return self.size

    def on_drag_start(self, event):
        self.properties.destroy_children()
        self.properties.add_option(self.properties.GEOMETRY_CONTENT, "ID", "SINGLELINE_TEXT", "id", {"val": self.name, "callback": lambda val: (self.properties.main.hierarchy.update_text(self.name, val), self.change_name(val))})
        self.properties.add_option(self.properties.GEOMETRY_CONTENT, "Width", "SPINBOX", "Width", {"to": 500, "from": 0, "val": int(self.cget("width")), "callback": lambda val: self.save(lambda val: self.configure(width=val), "width", int(val), int(val))})
        self.properties.add_option(self.properties.GEOMETRY_CONTENT, "Height", "SPINBOX", "Height", {"to": 500, "from": 0, "val": int(self.cget("height")), "callback": lambda val: self.save(lambda val: self.configure(height=val), "height", int(val), int(val))})
        self.properties.add_option(self.properties.GEOMETRY_CONTENT, "Text", "TEXT", "text", {"val": self.cget("text"), "callback": lambda val: self.save(lambda val: self.configure(text=val), "text", val, val)})
        self.properties.add_option(self.properties.GEOMETRY_CONTENT, "Image", "IMAGE", "image", {"image": self.image, "size":self.get_size ,"key": "image", "callback": self.set_image})
        self.properties.add_option(self.properties.GEOMETRY_CONTENT, "Corner Radius", "SPINBOX", "Corner Radius", {"to": 100, "from": 0, "val": self.cget("corner_radius"), "callback": lambda val: self.save(lambda val: self.configure(corner_radius=val), "corner_radius", int(val), int(val))})
        self.properties.add_option(self.properties.GEOMETRY_CONTENT, "Border Width", "SPINBOX", "Border Width", {"to": 100, "from": 0, "val": self.cget("border_width"), "callback": lambda val: self.save(lambda val: self.configure(border_width=val), "border_width", int(val), int(val))})
        self.properties.add_option(self.properties.GEOMETRY_CONTENT, "Border Spacing", "SPINBOX", "border_spacing", {"to": 100, "from": 0, "val": self.cget("border_spacing"), "callback": lambda val: self.save(lambda val: self.configure(border_spacing=val), "border_spacing", int(val), int(val))})
        # Had to reset the image for compound option to take effect
        self.properties.add_option(self.properties.ARRANGEMENT, "Compound", "COMBO", "compound", {"vals": ["top", "bottom", "left", "right"], "default": self.cget("compound"), "callback": lambda val: self.save(lambda val: (self.configure(compound=val, image=None), self.set_compound(self.image)), "compound", val, val)})
        self.properties.add_option(self.properties.ARRANGEMENT, "Anchor", "COMBO", "anchor", {"vals": ["n", "ne", "e", "se", "s", "sw", "w", "nw", "center"], "default": self.cget("anchor"), "callback": lambda val: self.save(lambda val: self.configure(anchor=val, image=None), "anchor", val, val)})
        self.properties.add_option(self.properties.STYLES, "Font Family", "FONT_FAMILY", "font_family", {"key": "font_family", "default": self.cget("font").cget("family"), "callback": lambda val: self.save(lambda val: self.cget("font").configure(family=val), "font_family", val, val)})
        self.properties.add_option(self.properties.STYLES, "Font Size", "SPINBOX", "font_size", {"to": 500, "from": -500, "val": self.cget("font").cget("size"), "callback": lambda val: self.save(lambda val: self.cget("font").configure(size=int(val)), "font_size", int(val), int(val))})
        self.properties.add_option(self.properties.STYLES, "Font Weight", "COMBO", "font_weight", {"vals": ["bold", "normal"], "default": self.cget("font").cget("weight"), "callback": lambda val: self.save(lambda val: self.cget("font").configure(weight=val), "font_weight", val, val)})
        self.properties.add_option(self.properties.STYLES, "Font Slant", "COMBO", "font_slant", {"vals": ["italic", "roman"], "default": self.cget("font").cget("slant"), "callback": lambda val: self.save(lambda val: self.cget("font").configure(slant=val), "font_slant", val, val)})
        self.properties.add_option(self.properties.STYLES, "Font Underline", "COMBO", "font_underline", {"vals": ["True", "False"], "default": str(bool(self.cget("font").cget("underline"))), "callback": lambda val: self.save(lambda val: self.cget("font").configure(underline=val), "font_underline", self._bool_change(val), self._bool_change(val))})
        self.properties.add_option(self.properties.STYLES, "Font Overstrike", "COMBO", "font_overstrike", {"vals": ["True", "False"], "default": str(bool(self.cget("font").cget("overstrike"))), "callback": lambda val: self.save(lambda val: self.cget("font").configure(overstrike=val), "font_overstrike", self._bool_change(val), self._bool_change(val))})
        self.properties.add_option(self.properties.STYLES, "Hover", "COMBO", "hover", {"vals": ["True", "False"], "default": str(bool(self.cget("hover"))), "callback": lambda val: self.save(lambda val: self.configure(hover=val), "hover", self._bool_change(val), self._bool_change(val))})
        self.properties.add_option(self.properties.STYLES, "State", "COMBO", "state", {"vals": ["normal", "disabled"], "default": self.cget("state"), "callback": lambda val: self.save(lambda val: self.configure(state=val), "state", val, val)})
        self.properties.add_option(self.properties.STYLES, "FG Color", "COLOR_COMBO", "fg_color", {"color": self.cget("fg_color"), "key": "fg_color", "transparent": True, "callback": lambda val: self.save(lambda val: self.configure(fg_color=val), "fg_color", val, val)})
        self.properties.add_option(self.properties.STYLES, "BG Color", "COLOR_COMBO", "bg_color", {"color": self.cget("bg_color"), "key": "bg_color", "transparent": True, "callback": lambda val: self.save(lambda val: self.configure(bg_color=val), "bg_color", val, val)})
        self.properties.add_option(self.properties.STYLES, "Border Color", "COLOR_COMBO", "border_color", {"color": self.cget("border_color"), "key": "border_color", "transparent": False, "callback": lambda val: self.save(lambda val: self.configure(border_color=val), "border_color", val, val)})
        self.properties.add_option(self.properties.STYLES, "Hover Color", "COLOR_COMBO", "hover_color", {"color": self.cget("hover_color"), "key": "hover_color", "transparent": False, "callback": lambda val: self.save(lambda val: self.configure(hover_color=val), "hover_color", val, val)})
        self.properties.add_option(self.properties.STYLES, "Text Color", "COLOR_COMBO", "text_color", {"color": self.cget("text_color"), "key": "text_color", "transparent": False, "callback": lambda val: self.save(lambda val: self.configure(text_color=val), "text_color", val, val)})
        self.properties.add_option(self.properties.STYLES, "Text Disabled Color", "COLOR_COMBO", "text_color_disabled", {"color": self.cget("text_color_disabled"), "key": "text_color_disabled", "transparent": False, "callback": lambda val: self.save(lambda val: self.configure(text_color_disabled=val), "text_color_disabled", val, val)})
        self.default()

    def set_image(self, img, size):
        if img is not None and img != "":
            self.image = img
            try:
                pil_img = Image.open(img)
                ctk_img = CTkImage(light_image=pil_img, dark_image=pil_img, size=size)
                self.configure(image=ctk_img)
                # Workarounds originais para atualizar o tamanho caso necessário
                self.configure(width=int(self.cget("width"))+1)
                self.configure(width=int(self.cget("width"))-1)
                self.img = img
                self.size = size
                self.props["image"] = img
            except Exception as e:
                print(f"[DEBUG] Erro ao carregar imagem do botão: {e}")
        else:
            self.image = None
            # Bloco original para tratar remoção de imagem sem quebrar a UI
            try:
                with_img_width = self.winfo_width()
                with_img_height = self.winfo_height()
                real_width = self.cget("width")
                real_height = self.cget("height")
                self.configure(image=None, width=with_img_width, height=with_img_height)
                self.update()
                self.configure(width=real_width, height=real_height)
                self.size = None
                if "image" in self.props:
                    self.props.pop("image")
            except Exception:
                pass

        self.update()
        if hasattr(self, 'properties') and self.properties and self.properties.main:
            self.properties.main.draw_box(self.properties.main.hierarchy.widget)

    def set_compound(self, image):
        if image is not None:
            self.set_image(image, self.size)
