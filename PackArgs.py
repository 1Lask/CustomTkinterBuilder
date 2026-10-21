class PackArgs:
    def __init__(self):
        self.options = {}
        self.pack_options = {}

    def set_options(self, val):
        self.options = val

    def redraw(self, **kwargs):
        # Re-apply pack options directly to this widget. MainWindow does not
        # implement a redraw() method; trying to call it breaks every pack
        # layout property callback (Fill, Expand, Side, Padx and Pady).
        options = dict(kwargs)
        options.pop("in", None)
        self.pack_options = dict(options)

        main = getattr(getattr(self, "properties", None), "main", None)
        if getattr(main, "layout_mode", "pack") != "pack":
            return

        try:
            # Update geometry options without removing/reinserting the widget.
            # pack_forget() followed by pack() can change the widget's order in
            # the layout, making another widget move under the pointer and get
            # selected while the user is editing Padx/Pady.
            self.pack_configure(**options)
        except Exception:
            # Keep the chosen values so they can be restored when pack mode
            # is active again, even if this widget cannot currently be packed.
            pass

    def default(self):
        # The layout properties must match the active geometry manager.
        # pack_info() raises TclError when the widget is currently managed by place().
        main = getattr(getattr(self, "properties", None), "main", None)
        if getattr(main, "layout_mode", "pack") == "place":
            try:
                info = self.place_info()
                x = int(float(info.get("x", self.winfo_x()) or 0))
                y = int(float(info.get("y", self.winfo_y()) or 0))
            except Exception:
                x, y = int(self.winfo_x()), int(self.winfo_y())

            def update_place(**changes):
                try:
                    self.place_configure(**changes)
                    current = self.place_info()
                    self.place_options = {
                        "x": int(float(current.get("x", x) or 0)),
                        "y": int(float(current.get("y", y) or 0)),
                        "width": max(1, int(self.cget("width"))),
                        "height": max(1, int(self.cget("height"))),
                    }
                except Exception:
                    pass

            self.properties.add_option(self.properties.LAYOUT, "X", "SPINBOX", "X", {
                "to": 10000, "from": 0, "val": x,
                "callback": lambda val: update_place(x=int(val))
            })
            self.properties.add_option(self.properties.LAYOUT, "Y", "SPINBOX", "Y", {
                "to": 10000, "from": 0, "val": y,
                "callback": lambda val: update_place(y=int(val))
            })
            self.properties.add_option(self.properties.LAYOUT, "Width", "SPINBOX", "Width", {
                "to": 10000, "from": 1, "val": max(1, int(self.winfo_width())),
                "callback": lambda val: (self.configure(width=int(val)), update_place(width=int(val)))
            })
            self.properties.add_option(self.properties.LAYOUT, "Height", "SPINBOX", "Height", {
                "to": 10000, "from": 1, "val": max(1, int(self.winfo_height())),
                "callback": lambda val: (self.configure(height=int(val)), update_place(height=int(val)))
            })
            return

        self.properties.add_option(self.properties.LAYOUT, "Fill", "COMBO", "Fill", {"vals": ["none", "x", "y", "both"], "default": str(self.pack_info()["fill"]), "callback": lambda val: self.redraw(fill=val, **{k: v for k, v in self.pack_info().items() if k != "fill"})})
        self.properties.add_option(self.properties.LAYOUT, "Expand", "COMBO", "Expand", {"vals": ["False", "True"], "default": str(bool(self.pack_info()["expand"])), "callback": lambda val: self.redraw(expand=self._bool_change(val), **{k: v for k, v in self.pack_info().items() if k != "expand"})})
        self.properties.add_option(self.properties.LAYOUT, "Side", "COMBO", "Side", {"vals": ["top", "bottom", "left", "right"], "default": str(self.pack_info()["side"]), "callback": lambda val: self.redraw(side=val, **{k: v for k, v in self.pack_info().items() if k != "side"})})

        if type(self.pack_info()["padx"]) == int:
            self.properties.add_option(self.properties.LAYOUT, "Padx", "TUPLE", "Padx", {"to": 500, "from": 0, "val1": int(self.pack_info()["padx"]), "val2": int(self.pack_info()["padx"]), "callback": lambda val1, val2: self.redraw(padx=(val1, val2), **{k: v for k, v in self.pack_info().items() if k != "padx"})})
        else:
            self.properties.add_option(self.properties.LAYOUT, "Padx", "TUPLE", "Padx", {"to": 500, "from": 0, "val1": int(self.pack_info()["padx"][0]), "val2": int(self.pack_info()["padx"][1]), "callback": lambda val1, val2: self.redraw(padx=(val1, val2), **{k: v for k, v in self.pack_info().items() if k != "padx"})})

        if type(self.pack_info()["pady"]) == int:
            self.properties.add_option(self.properties.LAYOUT, "Pady", "TUPLE", "Pady", {"to": 500, "from": 0, "val1": int(self.pack_info()["pady"]), "val2": int(self.pack_info()["pady"]), "callback": lambda val1, val2: self.redraw(pady=(val1, val2), **{k: v for k, v in self.pack_info().items() if k != "pady"})})
        else:
            self.properties.add_option(self.properties.LAYOUT, "Pady", "TUPLE", "Pady", {"to": 500, "from": 0, "val1": int(self.pack_info()["pady"][0]), "val2": int(self.pack_info()["pady"][1]), "callback": lambda val1, val2: self.redraw(pady=(val1, val2), **{k: v for k, v in self.pack_info().items() if k != "pady"})})
