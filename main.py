import json
import platform
import shutil
import threading
import tkinter.messagebox
import uuid
import sys
import os
from tkinter import messagebox
from tkinter.colorchooser import askcolor

import darkdetect
from Widgets import ThemedText
from Widgets import ThemedButton
from properties import PropertiesManager
from tkinter.filedialog import asksaveasfilename, askdirectory
from customtkinter import *
from dragndrop import DragManager
from Widgets.Button import Button
from Widgets.Label import Label
from Widgets.Frame import Frame
from Widgets.Entry import Entry
from Widgets.Switch import Switch
from Widgets.TextBox import TextBox
from Widgets.ProgressBar import ProgressBar
from Widgets.SegmentedButton import SegmentedButton
from Widgets.Slider import Slider
from Widgets.OptionMenu import OptionMenu
from Widgets.CheckBox import CheckBox
from Widgets.ScrollableFrame import ScrollableFrame
from Widgets.RadioButton import RadioButton
from Widgets.Scrollbar import Scrollbar
from Widgets.ComboBox import ComboBox
from Widgets.Main import Main
from CodeGenerator import CodeGenerator
from PIL import Image, ImageTk
from get_path import resource_path, tempify, joinpath, get_settings_path
from theme_colors import get_ui_color


def blockPrint():
    sys.stdout = open(os.devnull, 'w')
#blockPrint()

class ThemeUtl:
    def __init__(self, theme_dir, theme_name):
        path = resource_path(os.path.join(theme_dir, f"{theme_name}.json"))
        with open(path, "r") as f:
            self.theme = json.load(f)
        self.path = path
        self.name = theme_name

    def get_theme_by_name(self):
        return self.theme

class SaveFileDialog(CTkToplevel):
    def __init__(self, *args, callback, theme=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.callback = callback
        self.after(20, self.lift)
        self.after(25, self.focus_get)
        self.wm_iconbitmap()
        self.iconpath = ImageTk.PhotoImage(file=resource_path('Logo.ico'))
        self.after(100, lambda: self.iconphoto(False, self.iconpath))

        if theme:
            self.geometry("450x350+600+200")
            self.title("Novo Projeto")
        else:
            self.geometry("500x280+600+200")
            self.title("Salvar Projeto")

        self.project_name_lbl = CTkLabel(self, text="Nome do Projeto", anchor="w", padx=5, font=CTkFont(size=20))
        self.project_name_lbl.pack(pady=(20, 0), padx=20, fill="x")

        self.project_name_entry = CTkEntry(self, placeholder_text="Digite nome para o projeto")
        self.project_name_entry.pack(padx=20, pady=10, fill="x")
        self.project_name_entry.insert(0, "Sem título")

        self.fr = CTkFrame(self, fg_color="transparent")
        self.fr.pack(fill="x")

        self.dir_lbl = CTkLabel(self.fr, text="Local", anchor="w", padx=5, font=CTkFont(size=20))
        self.dir_lbl.pack(pady=(20, 10), padx=20, fill="x")

        self.dir_entry = CTkEntry(self.fr)
        self.dir_entry.pack(padx=(20, 5), pady=(0, 20), fill="x", side="left", expand=True)
        self.dir_entry.insert(0, os.path.expanduser("~/Documents"))
        self.dir_entry.configure(state="disabled")

        self.select_dir = CTkButton(self.fr, text="...", width=20, command=self.choose_dir)
        self.select_dir.pack(side="right", padx=(0, 20), pady=(0, 20))

        if theme:
            self.f = CTkFrame(self, fg_color="transparent")
            self.f.pack(fill="x")

            self.theme_lbl = CTkLabel(self.f, text="Theme", anchor="w", padx=5, font=CTkFont(size=20))
            self.theme_lbl.pack(pady=(20, 10), padx=20, fill="x")

            self.theme_entry = CTkOptionMenu(self.f, values=["green", "blue", "dark-blue"])
            self.theme_entry.pack(padx=20, pady=(0, 20), fill="x", side="left", expand=True)

            # Adicionado self.destroy() para fechar a janela ao salvar com tema
            self.save_btn = CTkButton(self, text="Salvar", height=35, command=lambda: (
                self.callback(dir_=self.dir_entry.get(), name=self.project_name_entry.get(), theme=self.theme_entry.get()), 
                self.destroy()
            ))
            self.save_btn.pack(fill="x", padx=20, pady=20)
        else:
            # Adicionado self.destroy() para fechar a janela no salvamento normal
            self.save_btn = CTkButton(self, text="Salvar", height=35, command=lambda: (
                self.callback(dir_=self.dir_entry.get(), name=self.project_name_entry.get()), 
                self.destroy()
            ))
            self.save_btn.pack(fill="x", padx=20, pady=20)

    def choose_dir(self):
        dir = askdirectory()
        if dir != "":
            self.dir_entry.configure(state="normal")
            self.dir_entry.delete(0, "end")
            self.dir_entry.insert(0, dir)
            self.dir_entry.configure(state="disabled")

class MainWindow:
    def __init__(self, root, theme_name):
        self.type = "ROOT"
        self.widgets = {}
        self.id_mapped_widgets = {}
        self.hierarchy = None
        self.r = root
        self.widgets[root] = {}
        self.drag_manager = None
        self.properties = None
        self._parents = []
        self.temp_widgets = {}
        self.file = ""
        self.total_num = 0
        self.files_to_copy = []
        self.title = "Window"
        self.theme_manager = ThemeUtl(theme_dir=f"Themes", theme_name=theme_name)
        self.horiz_max_offset = 100
        self.vert_max_offset = 100
        self.current_selected_widget = None
        self.layout_mode = "pack"
        self.theme = self.theme_manager.get_theme_by_name()
        self.widget_colors = {
            "CTk": ["fg_color"],
            "CTkToplevel": ["fg_color"],
            "CTkFrame": ["fg_color", "border_color"],
            "CTkButton": ["fg_color", "hover_color", "border_color", "text_color", "text_color_disabled"],
            "CTkLabel": ["fg_color", "text_color"],
            "CTkEntry": ["fg_color", "border_color", "text_color", "placeholder_text_color"],
            "CTkCheckBox": ["fg_color", "border_color", "hover_color", "checkmark_color", "text_color", "text_color_disabled"],
            "CTkSwitch": ["fg_color", "progress_color", "button_color", "button_hover_color", "text_color", "text_color_disabled"],
            "CTkRadioButton": ["fg_color", "border_color", "hover_color", "text_color", "text_color_disabled"],
            "CTkProgressBar": ["fg_color", "progress_color", "border_color"],
            "CTkSlider": ["fg_color", "progress_color", "button_color", "button_hover_color"],
            "CTkOptionMenu": ["fg_color", "button_color", "button_hover_color", "text_color", "text_color_disabled"],
            "CTkComboBox": ["fg_color", "border_color", "button_color", "button_hover_color", "text_color", "text_color_disabled"],
            "CTkScrollbar": ["fg_color", "button_color", "button_hover_color"],
            "CTkSegmentedButton": ["fg_color", "selected_color", "selected_hover_color", "unselected_color", "unselected_hover_color", "text_color", "text_color_disabled"],
            "CTkTextbox": ["fg_color", "border_color", "text_color", "scrollbar_button_color", "scrollbar_button_hover_color"],
            "CTkScrollableFrame": ["label_fg_color"],
            "DropdownMenu": ["fg_color", "hover_color", "text_color"]
        }

    def change_appearance_mode(self, mode):
        if mode == 0:
            mode = "light"
        else:
            mode = "dark"

        self.r._set_appearance_mode(mode)
        self.r.winfo_toplevel().main_window_panel._set_appearance_mode(mode)
        self.r.winfo_toplevel().temp._set_appearance_mode(mode)
        self.loop_change_appearance(mode, self.widgets[self.r])

    def loop_change_appearance(self, mode, d):
        for x in list(d.keys()):
            if d[x] != {}:
                x._set_appearance_mode(mode)
                self.loop_change_appearance(mode, d[x])
            else:
                x._set_appearance_mode(mode)

    def apply_theme_to_widget(self, widget):
        if self.appearance.get() == 0:
            mode = "light"
        else:
            mode = "dark"

        widget._set_appearance_mode(mode)

        if widget.get_class() == "CTkScrollableFrame":
            x = self.theme["CTkFrame"]
        else:
            x = self.theme[widget.get_class()]

        d = {}

        for key in list(x.keys()):
            if key == "top_fg_color":
                if widget.get_class() == "CTkFrame" or widget.get_class() == "CTkScrollableFrame":
                    try:
                        if widget.master.cget("fg_color") == x["fg_color"]:
                            d["fg_color"] = x["top_fg_color"]
                        else:
                            d["fg_color"] = x["fg_color"]
                    except tkinter.TclError:
                        if widget.master.master.master.master._fg_color == x["fg_color"]:
                            d["fg_color"] = x["top_fg_color"]
                        else:
                            d["fg_color"] = x["fg_color"]
            else:
                d[key] = x[key]

        if widget.__class__ not in [Frame, ProgressBar, Scrollbar, Slider, Main, ScrollableFrame]:
            for y in list(self.theme["CTkFont"].keys()):
                if sys.platform == "darwin":
                    d["font"] = CTkFont(family=self.theme["CTkFont"]["macOS"]["family"], size=self.theme["CTkFont"]["macOS"]["size"],
                                      weight=self.theme["CTkFont"]["macOS"]["weight"])
                elif sys.platform.startswith("win"):
                    d["font"] = CTkFont(family=self.theme["CTkFont"]["Windows"]["family"], size=self.theme["CTkFont"]["Windows"]["size"],
                                      weight=self.theme["CTkFont"]["Windows"]["weight"])
                else:
                    d["font"] = CTkFont(family=self.theme["CTkFont"]["Linux"]["family"], size=self.theme["CTkFont"]["Linux"]["size"],
                                      weight=self.theme["CTkFont"]["Linux"]["weight"])
        widget.configure(**d)

        if widget.get_class() == "CTkScrollableFrame":
            widget.configure(scrollbar_fg_color=self.theme["CTkScrollbar"]["fg_color"])

        if widget.__class__ in [ComboBox, OptionMenu]:
            widget.set_nonvisible_disable()

    def run_code(self):
        code = CodeGenerator(indentation="\t")
        code.add_line(f"""
root = CTkToplevel()
root.title("{self.escape_special_chars(self.title)}")
root.geometry("{self.r.cget('width')}x{self.r.cget('height')}")
root.protocol("WM_DELETE_WINDOW", lambda root=root: (set_default_color_theme("{resource_path(os.path.join('Themes', 'ctktheme.json'))}"), root.destroy()))
root.configure(fg_color="{self.r.cget("fg_color")[self.appearance.get()]}")
set_default_color_theme("{self.theme_manager.name}")
root.after(20, root.lift)
""")
        self.loop_generate(d=self.widgets[self.r], parent="root", code=code, run=True)
        exec(code.get_code())

    def export(self, code):
        filename = asksaveasfilename(filetypes=[(".py", "py")])
        if filename != "":
            with open(filename, "w", encoding="utf-8") as f:
                f.write(code)

    def export_code(self):
        code = CodeGenerator(indentation="    ")
        code.add_line(f"""
from customtkinter import *
from PIL import Image

set_default_color_theme("{self.theme_manager.name}")

root = CTk()
root.title("{self.escape_special_chars(self.title)}")
root.geometry("{self.r.cget('width')}x{self.r.cget('height')}")
root.configure(fg_color={self.r.cget("fg_color")})
""")
        self.loop_generate(d=self.widgets[self.r], parent="root", code=code)
        code.add_line("root.mainloop()")

        oop_code = CodeGenerator(indentation="    ")
        oop_code.add_line("""
from customtkinter import *
from PIL import Image

class App(CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
""")
        oop_code.indent()
        oop_code.indent()
        self.loop_generate_oop(d=self.widgets[self.r], parent="self", code=oop_code)
        oop_code.add_line(f"""
set_default_color_theme("{self.theme_manager.name}")
root = App()
root.geometry("{self.r.cget("width")}x{self.r.cget("height")}")
root.title("{self.escape_special_chars(self.title)}")
root.configure(fg_color={self.r.cget("fg_color")})
root.mainloop()
""")

        top = CTkToplevel()
        top.geometry("1000x800+500+100")
        top.title("Exportar Código")
        top.configure(fg_color=["gray95", "gray10"])
        top.after(20, top.lift)
        top.after(25, top.focus_get)
        top.wm_iconbitmap()
        top.iconpath = ImageTk.PhotoImage(file=resource_path('Logo.ico'))
        top.after(100, lambda: top.iconphoto(False, top.iconpath))

        self.codeviewer = CTkTextbox(top, font=CTkFont(family="Courier", size=14), wrap="none")
        self.codeviewer.pack(expand=True, fill="both", padx=20, pady=20)
        self.codeviewer.insert("1.0", oop_code.get_code())

        self.oop_code_switch = CTkSwitch(top, text="OOP Code", command=self.change_oop)
        self.oop_code_switch.pack(side="left", padx=20, pady=(0, 20))
        self.oop_code_switch.select()

        exp_btn = CTkButton(top, text="Exportar Código", command=lambda: self.export(self.current.get_code()))
        exp_btn.pack(side="right", padx=20, pady=(0, 20))

        self.current = oop_code
        self.not_current = code

    def change_oop(self):
        if self.oop_code_switch.get() == 0:
            code = self.not_current
            oop_code = self.current
            self.current = code
            self.not_current = oop_code
        else:
            oop_code = self.not_current
            code = self.current
            self.current = oop_code
            self.not_current = code
        self.codeviewer.delete("1.0", "end")
        self.codeviewer.insert("1.0", self.current.get_code())

    def escape_special_chars(self, text):
        escape_table = {
            "\n": "\\n",
            "\t": "\\t",
            "\"": "\\\"",
            "'": "\\'"
        }
        formatted_text = text
        for char, escape_seq in escape_table.items():
            formatted_text = formatted_text.replace(char, escape_seq)
        return formatted_text

    def loop_generate(self, d, parent, code, run=False):
        for x in list(d.keys()):
            if x.props == {}:
                code.add_line(f"{x.get_name()} = {x.get_class()}(master={parent})")
                if x.type == "FRAME" and not x._bool_change(x.propagate_on_pack):
                    code.add_line(f"{x.get_name()}.pack_propagate({x._bool_change(x.propagate_on_pack)})")
            else:
                p = ""
                font = "font=CTkFont("
                f2 = "hover_font=CTkFont("
                for key in list(x.props.keys()):
                    if key == "image" and x.props["image"] != None:
                        img_prop = x.props["image"]
                        img_path = ""
                        
                        if hasattr(img_prop, "cget"):
                            try:
                                img_path = img_prop.cget("dark_image").filename
                            except Exception:
                                pass
                        elif isinstance(img_prop, dict) and "image" in img_prop:
                            img_path = tempify(os.path.join("temp", img_prop["image"]))
                        elif isinstance(img_prop, str):
                            img_path = img_prop

                        size_tuple = (18, 18)
                        if hasattr(img_prop, "cget"):
                            try:
                                size_tuple = (img_prop.cget("size")[0], img_prop.cget("size")[1])
                            except Exception:
                                pass
                        elif isinstance(img_prop, dict) and "size" in img_prop:
                            size_tuple = (img_prop["size"][0], img_prop["size"][1])

                        if not run:
                            p += f'image=CTkImage(Image.open(r"{joinpath("Assets", os.path.basename(img_path))}"), size=({size_tuple[0]}, {size_tuple[1]})), '
                        else:
                            p += fr'image=CTkImage(Image.open(r"{img_path}"), size=({size_tuple[0]}, {size_tuple[1]})), '

                    elif key == "hover_image" and x.props["hover_image"] != None:
                        hover_prop = x.props["hover_image"]
                        hover_path = ""
                        
                        if hasattr(hover_prop, "cget"):
                            try:
                                hover_path = hover_prop.cget("dark_image").filename
                            except Exception:
                                pass
                        elif isinstance(hover_prop, str):
                            hover_path = hover_prop

                        size_tuple = (18, 18)
                        if hasattr(hover_prop, "cget"):
                            try:
                                size_tuple = (hover_prop.cget("size")[0], hover_prop.cget("size")[1])
                            except Exception:
                                pass

                        if not run:
                            p += f'hover_image=CTkImage(Image.open("{joinpath("Assets", os.path.basename(hover_path))}"), size=({size_tuple[0]}, {size_tuple[1]})), '
                        else:
                            p += f'hover_image=CTkImage(Image.open("{hover_path}"), size=({size_tuple[0]}, {size_tuple[1]})), '

                    elif key in ["font_family", "font_size", "font_weight", "font_slant", "font_underline", "font_overstrike"]:
                        if key == "font_family":
                            current_os = platform.system()
                            if current_os == "Darwin":
                                current_os = "macOS"
                            elif current_os == "Windows":
                                current_os = "Windows"
                            elif current_os == "Linux":
                                current_os = "Linux"
                            if x.props[key] == self.theme["CTkFont"][current_os]["family"]:
                                pass
                            else:
                                if type(x.props[key]) == str:
                                    font += f'{key[5::]}="{x.props[key]}", '
                                else:
                                    font += f'{key[5::]}={x.props[key]}, '
                        else:
                            if type(x.props[key]) == str:
                                font += f'{key[5::]}="{x.props[key]}", '
                            else:
                                font += f'{key[5::]}={x.props[key]}, '
                    elif key in ["hover_font_family", "hover_font_size", "hover_font_weight", "hover_font_slant", "hover_font_underline", "hover_font_overstrike"]:
                        if type(x.props[key]) == str:
                            f2 += f'{key[11::]}="{x.props[key]}", '
                        else:
                            f2 += f'{key[11::]}={x.props[key]}, '
                    else:
                        if type(x.props[key]) == str:
                            k = self.escape_special_chars(x.props[key])
                            p += f'{key}="{k}", '
                        elif type(x.props[key]) == tuple or type(x.props[key]) == list and len(x.props[key]) == 2:
                            if type(x.props[key][0]) == str and type(x.props[key][1]) == str:
                                p += f'{key}=("{x.props[key][0]}", "{x.props[key][1]}"), '
                            else:
                                p += f"{key}=({x.props[key][0]}, {x.props[key][1]}), "
                        else:
                            p += f"{key}={x.props[key]}, "

                font = font[0:-2]
                f2 = f2[0:-2]
                f2 += ")"
                font += ")"

                if font != "font=CTkFon)":
                    p += font
                    p += ", "
                if f2 != "hover_font=CTkFon)":
                    p += f2
                    p += ", "

                p = p[0:-2]
                code.add_line(f"{x.get_name()} = {x.get_class()}(master={parent}, {p})")
                if x.type == "FRAME" and not x._bool_change(x.propagate_on_pack):
                    code.add_line(f"{x.get_name()}.pack_propagate({x._bool_change(x.propagate_on_pack)})")

            if x.pack_options == {}:
                code.add_line(f"{x.get_name()}.pack()")
                if run:
                    if x.get_class() != "CTkSegmentedButton":
                        code.add_line(f"{x.get_name()}._set_appearance_mode('{'light' if self.appearance.get() == 0 else 'dark'}')")
                        if x.get_class() == "CTkScrollableFrame":
                            code.add_line(f"{x.get_name()}._parent_frame._set_appearance_mode('{'light' if self.appearance.get() == 0 else 'dark'}')")
                            code.add_line(f"{x.get_name()}._scrollbar._set_appearance_mode('{'light' if self.appearance.get() == 0 else 'dark'}')")
                    else:
                        code.add_line(f"""
for x in {x.get_name()}._buttons_dict.values():
    x._set_appearance_mode('{'light' if self.appearance.get() == 0 else 'dark'}')
""")
            else:
                p = ""
                default_pack_options = {"expand": False, "anchor": "center", "fill": "none", "padx": 0, "pady": 0, "side": "top", "ipadx": 0, "ipady": 0}
                modified_pack_options = x.pack_options
                for i in list(modified_pack_options.keys()):
                    if modified_pack_options[i] == default_pack_options[i]:
                        modified_pack_options.pop(i)

                for key in list(modified_pack_options.keys()):
                    if type(modified_pack_options[key]) == str:
                        p += f'{key}="{modified_pack_options[key]}", '
                    elif type(modified_pack_options[key]) == tuple or type(modified_pack_options[key]) == list:
                        p += f"{key}=({int(modified_pack_options[key][0])}, {int(modified_pack_options[key][1]  )}), "
                    else:
                        p += f"{key}={modified_pack_options[key]}, "

                p = p[0:-2]
                code.add_line(f"{x.get_name()}.pack({p})")
                if run:
                    code.add_line(f"{x.get_name()}._set_appearance_mode('{'light' if self.appearance.get() == 0 else 'dark'}')")
                    if x.get_class() == "CTkScrollableFrame":
                        code.add_line(f"{x.get_name()}._parent_frame._set_appearance_mode('{'light' if self.appearance.get() == 0 else 'dark'}')")
                        code.add_line(f"{x.get_name()}._scrollbar._set_appearance_mode('{'light' if self.appearance.get() == 0 else 'dark'}')")

            if d[x] != {}:
                self.loop_generate(d=d[x], parent=x.get_name(), code=code, run=run)

    def launch_thread_with_message(self, target, args=(), kwargs={}):
        def target_with_msg(*args, **kwargs):
            target(*args, **kwargs)
            self.hierarchy.update_list(self.widgets, 5)
            self.destroy_loading()

        self.show_loading()
        thread = threading.Thread(target=target_with_msg, args=args, kwargs=kwargs)
        thread.start()
        return thread

    def show_loading(self):
        m = self.r.winfo_toplevel()
        self.loading_frame = CTkFrame(m)
        self.loading_frame.place(x=0, y=0, relwidth=1, relheight=1)
        frm = CTkFrame(self.loading_frame, fg_color="transparent", width=700, height=50)
        frm.pack_propagate(False)
        txt_frame = CTkFrame(frm, fg_color="transparent")
        txt_frame.pack(pady=1, fill="x", expand=True, padx=100)
        self.edit_lbl = CTkLabel(txt_frame, text="Criando Widgets Editáveis....", font=CTkFont(size=15))
        self.edit_lbl.pack(side="left")
        self.lbl2 = CTkLabel(txt_frame, text=f"0/{self.widgetnumber.get()}", font=CTkFont(size=15))
        self.lbl2.pack(side="right")
        stepval = ((1/self.widgetnumber.get())*50)
        self.progressbar = CTkProgressBar(frm, height=15, orientation="horizontal", mode="determinate", determinate_speed=stepval)
        self.progressbar.set(0)
        self.progressbar.pack(fill="x", padx=100)
        frm.pack(expand=True)

    def destroy_loading(self):
        try:
            self.loading_frame.destroy()
        except Exception:
            pass

    def open_file(self):
        file = askdirectory()
        if file != "":
            self.close_current_project()
            self.file = [os.path.dirname(file), os.path.basename(file)]
            shutil.rmtree(tempify('temp'))
            shutil.copytree(os.path.join(file, "Assets"), tempify("temp"))

            with open(os.path.join(file, f"{os.path.basename(file)}.json"), 'r') as openfile:
                d = json.load(openfile)
            d = d["MAIN-FRAME-1"]

            self.r.props = d["parameters"]
            self.r._inner_id = d["ID"]
            for key in list(d["parameters"].keys()):
                if key == "width":
                    self.r.configure(width=d["parameters"]["width"])
                elif key == "height":
                    self.r.configure(height=d["parameters"]["height"])
                elif key == "fg_color":
                    self.r.configure(fg_color=d["parameters"]["fg_color"])
                elif key == "title":
                    self.title = d["parameters"]["title"]
            d.pop("TYPE")
            d.pop("parameters")
            d.pop("pack_options")
            d.pop("ID")

            self.theme_manager = ThemeUtl(theme_dir=f"Themes", theme_name=d["theme"])
            self.theme = self.theme_manager.get_theme_by_name()
            self.properties.color_manager.colors = d["palette"]
            self.properties.color_manager.on_change_list = d["palette_on_change"]
            d.pop("theme")
            d.pop("palette")
            d.pop("palette_on_change")
            self.current_widget_count = IntVar(value=0)
            self.current_widget_count.trace("w", self.changed_value)
            self.widgetnumber = IntVar(value=1)
            self.get_number_of_widgets(json.loads(json.dumps(d)))

            self.launch_thread_with_message(target=self.loop_open, args=(d, self.r))

    def changed_value(self, a, b, c):
        try:
            if (self.widgetnumber.get()-1) == self.current_widget_count.get():
                self.edit_lbl.configure(text="Atualizando Hierarquia....")
            self.lbl2.configure(text=f"{self.current_widget_count.get()}/{self.widgetnumber.get()}")
            self.progressbar.step()
        except Exception:
            pass

    def loop_open(self, d, parent, copy=False):
        for x in list(d.keys()):
            y = d[x]["TYPE"]
            if y == "FRAME":
                w = Frame
            elif y == "BUTTON":
                w = Button
            elif y == "LABEL":
                w = Label
            elif y == "SWITCH":
                w = Switch
            elif y == "SCROLLABLEFRAME":
                w = ScrollableFrame
            elif y == "ENTRY":
                w = Entry
            elif y == "MAIN":
                w = Main
            elif y == "TEXTBOX":
                w = TextBox
            elif y == "PROGRESSBAR":
                w = ProgressBar
            elif y == "SEGMENTEDBUTTON":
                w = SegmentedButton
            elif y == "SLIDER":
                w = Slider
            elif y == "OPTIONMENU":
                w = OptionMenu
            elif y == "CHECKBOX":
                w = CheckBox
            elif y == "RADIOBUTTON":
                w = RadioButton
            elif y == "SCROLLBAR":
                w = Scrollbar
            elif y == "COMBOBOX":
                w = ComboBox
            else:
                raise ModuleNotFoundError(f"[DEBUG] O widget não está disponível. O widget desconhecido era {x}")
            f = CTkFont()

            family = False
            d_copy = dict(d[x]["parameters"])
            img_path = None
            img_size = None

            for p in list(d[x]["parameters"]):
                if p == "image":
                    img_data = d[x]["parameters"]["image"]
                    if isinstance(img_data, dict):
                        file_name = img_data.get("image")
                        img_size = img_data.get("size", [18, 18])
                    else:
                        file_name = str(img_data)
                        img_size = [18, 18]
                    
                    if file_name:
                        full_img_path = tempify(os.path.join("temp", file_name))
                        if os.path.exists(full_img_path):
                            img_path = full_img_path
                    d[x]["parameters"].pop("image")
                elif p == "font_family":
                    f.configure(family=d[x]["parameters"][p])
                    family = True
                    d[x]["parameters"].pop("font_family")
                    if w != ScrollableFrame:
                        d[x]["parameters"]["font"] = f
                    else:
                        d[x]["parameters"]["label_font"] = f
                elif p == "font_size":
                    f.configure(size=d[x]["parameters"][p])
                    d[x]["parameters"].pop("font_size")
                    if w != ScrollableFrame:
                        d[x]["parameters"]["font"] = f
                    else:
                        d[x]["parameters"]["label_font"] = f
                elif p == "font_weight":
                    f.configure(weight=d[x]["parameters"][p])
                    d[x]["parameters"].pop("font_weight")
                    if w != ScrollableFrame:
                        d[x]["parameters"]["font"] = f
                    else:
                        d[x]["parameters"]["label_font"] = f
                elif p == "font_slant":
                    f.configure(slant=d[x]["parameters"][p])
                    d[x]["parameters"].pop("font_slant")
                    if w != ScrollableFrame:
                        d[x]["parameters"]["font"] = f
                    else:
                        d[x]["parameters"]["label_font"] = f
                elif p == "font_underline":
                    f.configure(underline=d[x]["parameters"][p])
                    d[x]["parameters"].pop("font_underline")
                    if w != ScrollableFrame:
                        d[x]["parameters"]["font"] = f
                    else:
                        d[x]["parameters"]["label_font"] = f
                elif p == "font_overstrike":
                    f.configure(overstrike=d[x]["parameters"][p])
                    d[x]["parameters"].pop("font_overstrike")
                    if w != ScrollableFrame:
                        d[x]["parameters"]["font"] = f
                    else:
                        d[x]["parameters"]["label_font"] = f

            if d[x]["parameters"] != {}:
                if "orientation" in list(d[x]["parameters"].keys()):
                    if parent.get_class() == "CTkScrollableFrame":
                        new_widget = w(master=parent.scrollwindow, orientation=d[x]["parameters"]["orientation"], properties=self.r.properties)
                    else:
                        new_widget = w(master=parent, orientation=d[x]["parameters"]["orientation"], properties=self.r.properties)
                    g = dict(d)
                    g[x]["parameters"].pop("orientation")
                    self.apply_theme_to_widget(new_widget)
                    new_widget.configure(**g[x]["parameters"])
                else:
                    if parent.get_class() == "CTkScrollableFrame":
                        new_widget = w(master=parent.scrollwindow, properties=self.r.properties)
                    else:
                        new_widget = w(master=parent, properties=self.r.properties)
                    self.apply_theme_to_widget(new_widget)
                    new_widget.configure(**d[x]["parameters"])

                try:
                    if img_path is not None and img_size is not None and os.path.exists(img_path):
                        loaded_img = CTkImage(light_image=Image.open(img_path), dark_image=Image.open(img_path), size=(img_size[0], img_size[1]))
                        new_widget.configure(image=loaded_img)
                        d_copy["image"] = loaded_img
                except Exception as e:
                    print(f"[DEBUG] Erro ao renderizar imagem no botão {x}: {e}")

                new_widget.props = d_copy
            else:
                if parent.get_class() == "CTkScrollableFrame":
                    new_widget = w(master=parent.scrollwindow, properties=self.r.properties)
                else:
                    new_widget = w(master=parent, properties=self.r.properties)
                self.apply_theme_to_widget(new_widget)

            new_widget.num = self.total_num
            if not copy:
                new_widget.name = x
            else:
                new_widget.name = new_widget.type + str(new_widget.num + 1) + "_copy"
            self.total_num += 1
            self._parents = []

            self.get_parents(new_widget)
            if family:
                new_widget.family = new_widget.cget("font").cget("family")

            self.add_to_dict(self.widgets, self._parents, new_widget)
            self._parents = []

            new_widget.pack_options = d[x].get("pack_options", {}) or {}
            new_widget.place_options = d[x].get("place_options", {}) or {}
            if self.layout_mode == "place":
                po = new_widget.place_options or {"x":10,"y":10,"width":max(80,new_widget.winfo_reqwidth()),"height":max(28,new_widget.winfo_reqheight())}
                new_widget.place(**po); new_widget.place_options = po; self.bind_free_drag(new_widget)
            else: new_widget.pack(**new_widget.pack_options)

            if new_widget.__class__ == SegmentedButton:
                new_widget.configure(command=lambda e, nw=new_widget: (nw.on_drag_start(None), self.hierarchy.set_current_selection(nw)))
            elif new_widget.__class__ == ScrollableFrame:
                new_widget.scrollwindow.bind("<Button-1>", lambda e, nw=new_widget: (nw.on_drag_start(None), self.hierarchy.set_current_selection(nw)))
                new_widget.canv.bind("<Button-1>", lambda e, nw=new_widget: (nw.on_drag_start(None), self.hierarchy.set_current_selection(nw)))
            else:
                new_widget.bind("<Button-1>", lambda e, nw=new_widget: (nw.on_drag_start(None), self.hierarchy.set_current_selection(nw)))

            if new_widget.__class__ in [ComboBox, OptionMenu]:
                try:
                    new_widget.set(d_copy["values"][0])
                except KeyError as e:
                    print(e)

            if not copy:
                new_widget._inner_id = d[x]["ID"]
                self.id_mapped_widgets[new_widget._inner_id] = new_widget
            else:
                new_widget._inner_id = str(uuid.uuid4())
                self.id_mapped_widgets[new_widget._inner_id] = new_widget
                arr = self.properties.color_manager.get_all_changes(d[x]["ID"])
                for i in arr:
                    ar = self.properties.color_manager.on_change_list[i[0]]
                    ar.append([new_widget._inner_id, i[1][1], i[1][2]])
                    self.properties.color_manager.on_change_list[i[0]] = ar
            if new_widget.__class__ == Frame:
                new_widget.change_pack_propagate(d[x]["PACK_PROPAGATE"])
                d[x].pop("PACK_PROPAGATE")

            if new_widget.__class__ != SegmentedButton:
                self.drag_manager.update_children(children=parent.winfo_children())

            d[x].pop("TYPE")
            d[x].pop("pack_options", None)
            d[x].pop("place_options", None)
            d[x].pop("parameters")
            d[x].pop("ID")

            if hasattr(self, 'current_widget_count') and self.current_widget_count is not None:
                try:
                    self.current_widget_count.set(self.current_widget_count.get()+1)
                except Exception:
                    pass

            if d[x] != {}:
                self.loop_open(d[x], new_widget, copy=copy)

    def get_number_of_widgets(self, d):
        for x in list(d.keys()):
            y = d[x]["TYPE"]
            if y == "FRAME":
                d[x].pop("PACK_PROPAGATE")
            d[x].pop("TYPE")
            d[x].pop("pack_options")
            d[x].pop("parameters")
            d[x].pop("ID")
            self.widgetnumber.set(self.widgetnumber.get()+1)
            if d[x] != {}:
                self.get_number_of_widgets(d[x])

    def save(self, dir_, name):
        try:
            os.mkdir(path=os.path.join(dir_, name))
            os.mkdir(path=os.path.join(os.path.join(dir_, name), "Assets"))

            self.s = {self.r.get_name(): {}}
            self.loop_save(self.widgets, self.r.get_name(), self.s)
            self.s = self.s[self.r.get_name()]
            self.s[self.r.get_name()]["theme"] = self.theme_manager.name
            self.s[self.r.get_name()]["palette_on_change"] = self.properties.color_manager.on_change_list
            self.s[self.r.get_name()]["palette"] = self.properties.color_manager.colors
            self.file = [dir_, name]
            json_object = json.dumps(self.s, indent=4)
            with open(os.path.join(os.path.join(dir_, name), f"{name}.json"), "w") as outfile:
                outfile.write(json_object)

            self.r.winfo_toplevel().title(f"Custom Tkinter Builder 2.0 - {os.path.join(dir_, name)}")

            with open(get_settings_path(), 'r') as openfile:
                configure = json.load(openfile)

            self.project_files = configure["project_files"]
            self.project_files.append({"Name": name, "Directory": dir_})
            configure["project_files"] = self.project_files
            json_object = json.dumps(configure, indent=4)
            with open(get_settings_path(), 'w') as f:
                f.write(json_object)
            short_name = name[0:2].upper()
            try:
                main_app = self.r
                while hasattr(main_app, "master") and main_app.master is not None and not hasattr(main_app, "show_project"):
                    main_app = main_app.master
                    
                if hasattr(main_app, "show_project"):
                    main_app.show_project(short_name, name, dir_)
                else:
                    print("[DEBUG] Janela principal salva com sucesso.")
            except Exception as e:
                print(f"[DEBUG] Erro ao atualizar exibição do projeto: {e}")
                messagebox.showinfo("Salvo", "Arquivo salvo com sucesso")
        except FileExistsError:
            self.file = ""
            tkinter.messagebox.showerror("Error", f"File Exists: {os.path.join(dir_, name)}")

    def set_file(self, dir_, name):
        self.file = [dir_, name]
        self.save(dir_, name)

    def save_file(self):
        if self.file == "":
            SaveFileDialog(callback=self.set_file)

        if self.file != "":
            shutil.rmtree(os.path.join(os.path.join(self.file[0], self.file[1]), "Assets"))
            os.mkdir(path=os.path.join(os.path.join(self.file[0], self.file[1]), "Assets"))
            self.s = {self.r.get_name(): {}}
            self.loop_save(self.widgets, self.r.get_name(), self.s)
            self.s = self.s[self.r.get_name()]
            self.s[self.r.get_name()]["theme"] = self.theme_manager.name
            self.s[self.r.get_name()]["palette_on_change"] = self.properties.color_manager.on_change_list
            self.s[self.r.get_name()]["palette"] = self.properties.color_manager.colors
            json_object = json.dumps(self.s, indent=4)
            with open(os.path.join(os.path.join(self.file[0], self.file[1]), f"{self.file[1]}.json"), "w") as outfile:
                outfile.write(json_object)
            messagebox.showinfo("Salvo", "Arquivo salvo com sucesso")

    def saveas_file(self):
        SaveFileDialog(callback=self.save)

    def loop_save(self, d, parent, code):
        for x in list(d.keys()):
            props = dict(x.props)
            if "image" in list(props.keys()):
                img = ""
                img_prop = x.props.get("image")
                try:
                    if hasattr(img_prop, "cget"):
                        img_path = img_prop.cget("dark_image").filename
                        img = os.path.basename(img_path)
                        if img_path and os.path.exists(img_path):
                            shutil.copy2(img_path, os.path.join(self.file[0], self.file[1], "Assets"))
                    elif isinstance(img_prop, str):
                        img = os.path.basename(img_prop)
                        if os.path.exists(img_prop):
                            shutil.copy2(img_prop, os.path.join(self.file[0], self.file[1], "Assets"))
                except Exception as e:
                    print(f"[DEBUG] Erro ao processar imagem no loop_save: {e}")
                
                size = getattr(x, "size", [100, 100])
                props["image"] = {"image": img, "size": size}

            if "font_family" in list(props.keys()):
                current_os = platform.system()
                if current_os == "Darwin":
                    current_os = "macOS"
                elif current_os == "Windows":
                    current_os = "Windows"
                elif current_os == "Linux":
                    current_os = "Linux"
                if props["font_family"] == self.theme["CTkFont"][current_os]["family"]:
                    props.pop("font_family")

            place_options = getattr(x, "place_options", {}) or {}
            if self.layout_mode == "place": place_options = {"x":int(x.winfo_x()),"y":int(x.winfo_y()),"width":max(1,int(x.winfo_width())),"height":max(1,int(x.winfo_height()))}
            if x.get_class() == "CTkFrame":
                code[parent][x.get_name()] = {"TYPE": x.type, "parameters": props, "pack_options": getattr(x,"pack_options",{}), "place_options": place_options, "ID": x._inner_id, "PACK_PROPAGATE": x.propagate_on_pack}
            else:
                code[parent][x.get_name()] = {"TYPE": x.type, "parameters": props, "pack_options": getattr(x,"pack_options",{}), "place_options": place_options, "ID": x._inner_id}

            if d[x] != {}:
                self.loop_save(d[x], x.get_name(), code[parent])

    def loop_generate_oop(self, d, parent, code):
        for x in list(d.keys()):
            if x.props == {}:
                code.add_line(f"self.{x.get_name()} = {x.get_class()}(master={parent})")
                if x.type == "FRAME" and not x._bool_change(x.propagate_on_pack):
                    code.add_line(f"self.{x.get_name()}.pack_propagate({x._bool_change(x.propagate_on_pack)})")
            else:
                p = ""
                font = "font=CTkFont("
                f2 = "hover_font=CTkFont("
                for key in list(x.props.keys()):
                    if key == "image" and x.props["image"] != None:
                        p += f'image=CTkImage(Image.open(r"{os.path.join("Assets", os.path.basename(x.props["image"].cget("dark_image").filename))}"), size=({x.props["image"].cget("size")[0]}, {x.props["image"].cget("size")[1]})), '
                    elif key == "hover_image":
                        p += f'hover_image=CTkImage(Image.open("{os.path.join("Assets", os.path.basename(x.props["hover_image"].cget("dark_image").filename))}"), size=({x.props["hover_image"].cget("size")[0]}, {x.props["hover_image"].cget("size")[1]})), '
                    elif key in ["font_family", "font_size", "font_weight", "font_slant", "font_underline", "font_overstrike"]:
                        if key == "font_family":
                            current_os = platform.system()
                            if current_os == "Darwin":
                                current_os = "macOS"
                            elif current_os == "Windows":
                                current_os = "Windows"
                            elif current_os == "Linux":
                                current_os = "Linux"
                            if x.props[key] == self.theme["CTkFont"][current_os]["family"]:
                                pass
                            else:
                                if type(x.props[key]) == str:
                                    font += f'{key[5::]}="{x.props[key]}", '
                                else:
                                    font += f'{key[5::]}={x.props[key]}, '
                        else:
                            if type(x.props[key]) == str:
                                font += f'{key[5::]}="{x.props[key]}", '
                            else:
                                font += f'{key[5::]}={x.props[key]}, '
                    elif key in ["hover_font_family", "hover_font_size", "hover_font_weight", "hover_font_slant", "hover_font_underline", "hover_font_overstrike"]:
                        if type(x.props[key]) == str:
                            f2 += f'{key[11::]}="{x.props[key]}", '
                        else:
                            f2 += f'{key[11::]}={x.props[key]}, '
                    else:
                        if type(x.props[key]) == str:
                            k = self.escape_special_chars(x.props[key])
                            p += f'{key}="{k}", '
                        elif type(x.props[key]) == tuple or type(x.props[key]) == list and len(x.props[key]) == 2:
                            if type(x.props[key][0]) == str and type(x.props[key][1]) == str:
                                p += f'{key}=("{x.props[key][0]}", "{x.props[key][1]}"), '
                            else:
                                p += f"{key}=({x.props[key][0]}, {x.props[key][1]}), "
                        else:
                            p += f"{key}={x.props[key]}, "

                font = font[0:-2]
                f2 = f2[0:-2]
                f2 += ")"
                font += ")"
                if font != "font=CTkFon)":
                    p += font
                    p += ", "
                if f2 != "hover_font=CTkFon)":
                    p += f2
                    p += ", "

                p = p[0:-2]
                code.add_line(f"self.{x.get_name()} = {x.get_class()}(master={parent}, {p})")
                if x.type == "FRAME" and not x._bool_change(x.propagate_on_pack):
                    code.add_line(f"self.{x.get_name()}.pack_propagate({x._bool_change(x.propagate_on_pack)})")

            if x.pack_options == {}:
                code.add_line(f"self.{x.get_name()}.pack()")
            else:
                p = ""
                default_pack_options = {"expand": False, "anchor": "center", "fill": "none", "padx": 0, "pady": 0, "side": "top", "ipadx": 0, "ipady": 0}
                modified_pack_options = x.pack_options
                for i in list(modified_pack_options.keys()):
                    if modified_pack_options[i] == default_pack_options[i]:
                        modified_pack_options.pop(i)
                for key in list(modified_pack_options.keys()):
                    if type(modified_pack_options[key]) == str:
                        p += f'{key}="{modified_pack_options[key]}", '
                    elif type(modified_pack_options[key]) == tuple or type(modified_pack_options[key]) == list:
                        p += f"{key}=({int(modified_pack_options[key][0])}, {int(modified_pack_options[key][1])}), "
                    else:
                        p += f"{key}={modified_pack_options[key]}, "

                p = p[0:-2]
                code.add_line(f"self.{x.get_name()}.pack({p})")

            if d[x] != {}:
                self.loop_generate_oop(d=d[x], parent="self." + x.get_name(), code=code)

    def get_parents(self, widget):
        if widget == self.r:
            self._parents.reverse()
            pass
        else:
            if not widget.master.__repr__().startswith("<"):
                self._parents.append(widget.master)
                self.get_parents(widget.master)
            else:
                self.get_parents(widget.master)

    def add_to_dict(self, my_dict, key_list, value):
        current_dict = my_dict
        for key in key_list[:-1]:
            current_dict = current_dict[key]

        if current_dict[key_list[-1]] != {}:
            current_dict[key_list[-1]][value] = {}
            value.order = len(current_dict[key_list[-1]])
        else:
            current_dict[key_list[-1]] = {value: {}}
            value.order = 1

    def get_first_degree_parent(self, my_dict, key_list):
        current_dict = my_dict
        for key in key_list[:-1]:
            current_dict = current_dict[key]
        return current_dict[key_list[-1]]

    def simple_order_dict(self, data_dict):
        return dict(sorted(data_dict.items(), key=lambda item: getattr(item[0], 'order', 0)))

    def loop_order_sort(self, d):
        new_d = self.simple_order_dict(d)
        for key in new_d:
            value = new_d[key]
            if value != {}:
                new_d[key] = self.loop_order_sort(value)
        return new_d

    def set_layout_mode(self, mode):
        mode = "place" if mode in (True, "place", "free") else "pack"
        if mode == self.layout_mode: return
        for widget, children in list(self.widgets[self.r].items()): self._switch_tree(widget, children, mode)
        self.layout_mode = mode

    def _switch_tree(self, widget, children, mode):
        try:
            widget.update_idletasks()
            if mode == "place":
                widget.pack_options = dict(widget.pack_info())
                po = {"x": int(widget.winfo_x()), "y": int(widget.winfo_y()), "width": max(1,int(widget.winfo_width())), "height": max(1,int(widget.winfo_height()))}
                widget.pack_forget(); widget.place(**po); widget.place_options = po; self.bind_free_drag(widget)
            else:
                widget.place_forget(); widget.pack(**(getattr(widget,"pack_options",{}) or {"padx":(0,0),"pady":(0,0)}))
        except Exception: pass
        for child, grandchildren in list(children.items()): self._switch_tree(child, grandchildren, mode)

    def bind_free_drag(self, widget):
        if getattr(widget, "_free_drag_bound", False): return
        widget._free_drag_bound = True
        def start(e):
            if self.layout_mode == "place": widget._free_drag_start = (e.x_root,e.y_root,widget.winfo_x(),widget.winfo_y())
        def move(e):
            if self.layout_mode != "place" or not getattr(widget,"_free_drag_start",None): return
            sx,sy,x0,y0 = widget._free_drag_start
            x,y = max(0,x0+e.x_root-sx),max(0,y0+e.y_root-sy)
            widget.place_configure(x=x,y=y)
            widget.place_options = {"x":int(x),"y":int(y),"width":max(1,widget.winfo_width()),"height":max(1,widget.winfo_height())}
        def stop(e): widget._free_drag_start = None
        widget.bind("<ButtonPress-1>",start,add="+"); widget.bind("<B1-Motion>",move,add="+"); widget.bind("<ButtonRelease-1>",stop,add="+")
    def add_widget(self, w, properties, widget, x=0, y=0):
        if widget.master.master.__class__ == ScrollableFrame:
            new_widget = w(master=widget.master.master.get_me(), **properties)
        elif widget.master.master.master.__class__ == ScrollableFrame:
            new_widget = w(master=widget.master.master.master.get_me(), **properties)
        else:
            if widget.master.__class__ not in [ScrollableFrame, Frame, Main]:
                new_widget = w(master=widget.master.master, **properties)
            else:
                new_widget = w(master=widget.master, **properties)

        new_widget.num = self.total_num
        new_widget.name = new_widget.type + str(new_widget.num)
        self.apply_theme_to_widget(new_widget)
        new_widget._set_appearance_mode('light' if self.appearance.get() == 0 else 'dark')
        if new_widget.__class__ == Slider or new_widget.__class__ == Scrollbar or new_widget.__class__ == ScrollableFrame:
            new_widget.props["orientation"] = properties["orientation"]

        self.total_num += 1
        self.get_parents(new_widget)
        self.add_to_dict(self.widgets, self._parents, new_widget)
        self.id_mapped_widgets[new_widget._inner_id] = new_widget
        self._parents = []
        new_widget.configure(bg_color="transparent")
        new_widget.pack_options = getattr(new_widget, "pack_options", {}) or {"padx": (0,0), "pady": (0,0)}
        if self.layout_mode == "place":
            mx = new_widget.master.winfo_rootx() - self.r.winfo_rootx(); my = new_widget.master.winfo_rooty() - self.r.winfo_rooty()
            po = {"x":max(0,int(x-mx)),"y":max(0,int(y-my)),"width":max(80,new_widget.winfo_reqwidth()),"height":max(28,new_widget.winfo_reqheight())}
            new_widget.place(**po); new_widget.place_options = po; self.bind_free_drag(new_widget)
        else: new_widget.pack(padx=(0, 0), pady=(0, 0))

        if new_widget.__class__ == SegmentedButton:
            new_widget.configure(command=lambda e, nw=new_widget: (nw.on_drag_start(None), self.hierarchy.set_current_selection(nw)))
        elif new_widget.__class__ == ScrollableFrame:
            new_widget.scrollwindow.bind("<Button-1>", lambda e, nw=new_widget: (nw.on_drag_start(None), self.hierarchy.set_current_selection(nw)))
            new_widget.canv.bind("<Button-1>", lambda e, nw=new_widget: (nw.on_drag_start(None), self.hierarchy.set_current_selection(nw)))
        else:
            new_widget.bind("<Button-1>", lambda e, nw=new_widget: (nw.on_drag_start(None), self.hierarchy.set_current_selection(nw)))

        self.hierarchy.delete_children()
        self.hierarchy.update_list(self.widgets, 5)

        if new_widget.__class__ != SegmentedButton:
            if widget.master.master.__class__ == ScrollableFrame:
                self.drag_manager.update_children(children=widget.master.master.winfo_children())
            elif widget.master.master.master.__class__ == ScrollableFrame:
                self.drag_manager.update_children(children=widget.master.master.master.winfo_children())
            else:
                self.drag_manager.update_children(children=widget.master.winfo_children())

    def delete_from_dict(self, my_dict, key_list, value):
        current_dict = my_dict
        for key in key_list[:-1]:
            current_dict = current_dict[key]
        if current_dict[key_list[-1]] != {}:
            current_dict[key_list[-1]].pop(value)

    def show_palette(self, properties):
        PaletteEditor(color_manager=properties)

    def map_range(self, value, start1, stop1, start2, stop2):
        return start2 + (stop2 - start2) * ((value - start1) / (stop1 - start1))

    def on_vert_scrl(self, e):
        y = self.map_range(e, -100, 100, -self.vert_max_offset, self.vert_max_offset)
        self.r.place(y=y)
        self.r.winfo_toplevel().update()
        if self.current_selected_widget != None:
            self.draw_box(self.current_selected_widget)

    def on_vert_mouse(self, e):
        y = self.vert_scrl.get()
        y += e.delta
        y = max(-100, min(y, 100))
        self.vert_scrl.set(y)
        y = self.map_range(y, -100, 100, -self.vert_max_offset, self.vert_max_offset)
        self.r.place(y=y)
        self.r.winfo_toplevel().update()
        if self.current_selected_widget != None:
            self.draw_box(self.current_selected_widget)

    def on_horiz_scrl(self, e):
        x = self.map_range(e, -100, 100, -self.horiz_max_offset, self.horiz_max_offset)
        self.r.place(x=x)
        self.r.winfo_toplevel().update()
        if self.current_selected_widget != None:
            self.draw_box(self.current_selected_widget)

    def on_horiz_mouse(self, e):
        x = self.horiz_scrl.get()
        x += e.delta
        x = max(-100, min(x, 100))
        self.horiz_scrl.set(x)
        x = self.map_range(x, -100, 100, -self.horiz_max_offset, self.horiz_max_offset)
        self.r.place(x=x)
        self.r.winfo_toplevel().update()
        if self.current_selected_widget != None:
            self.draw_box(self.current_selected_widget)

    def get_x(self, widget):
        x = widget.winfo_x()
        y = 0
        if widget.master != self.r.master:
            y = self.get_x(widget.master)
        return x + y

    def get_y(self, widget):
        x = widget.winfo_y()
        y = 0
        if widget.master != self.r.master:
            y = self.get_y(widget.master)
        return x + y

    def draw_box(self, widget):
        if widget is not None:
            self.current_selected_widget = widget
            pad = 5
            x = self.get_x(widget) - pad
            y = self.get_y(widget) - pad
            parent = self.r.master
            width = widget.winfo_width() + (pad * 2)
            height = widget.winfo_height() + (pad * 2)
            self.destroy_box()
            self.left_box = CTkFrame(parent, width=2, height=height, fg_color="red", bg_color="red")
            self.left_box.place(x=x, y=y, anchor="nw")
            self.right_box = CTkFrame(parent, width=2, height=height, fg_color="red", bg_color="red")
            self.right_box.place(x=x+width, y=y, anchor="ne")
            self.top_box = CTkFrame(parent, width=width, height=2, fg_color="red", bg_color="red")
            self.top_box.place(x=x, y=y, anchor="nw")
            self.bottom_box = CTkFrame(parent, width=width, height=2, fg_color="red", bg_color="red")
            self.bottom_box.place(x=x, y=y+height, anchor="sw")

    def destroy_box(self):
        try:
            self.left_box.destroy()
            self.right_box.destroy()
            self.top_box.destroy()
            self.bottom_box.destroy()
        except Exception:
            pass

    def close_current_project(self):
        try:
            for widget in list(self.id_mapped_widgets.values()):
                try:
                    if widget != self.r:
                        widget.destroy()
                except Exception:
                    pass
            self.widgets = {}
            if hasattr(self, 'r') and self.r:
                self.widgets[self.r] = {}
                
            self.id_mapped_widgets = {}
            self._parents = []
            self.total_num = 0
            self.file = ""
            self.title = "Window"
            
            if self.hierarchy:
                self.hierarchy.delete_children()
            
            self.destroy_box()
            
        except Exception as e:
            print(f"[DEBUG] Erro ao fechar projeto anterior: {e}")

class WidgetButton(CTkButton):
    def __init__(self, on_drag, **kwargs):
        self.on_drag = on_drag
        super().__init__(**kwargs)
        self.configure(fg_color=(get_ui_color("legacy_dark"), get_ui_color("legacy_dark")), border_width=1, border_color=get_ui_color("pair_primary"), height=40)

    def pack(self, **kwargs):
        try:
            self.master.master.master.master.master.dragndrop_list.append(self)
        except AttributeError:
            try:
                self.master.master.master.master.master.master.dragndrop_list.append(self)
            except AttributeError:
                self.master.master.master.master.master.master.master.dragndrop_list.append(self)
        super().pack(**kwargs)

class Hierarchy(CTkScrollableFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.change_parent_selection = None
        self.current_selection = None
        self.widget = None
        self.main = None
        self.mainwindow = None
        self.btns = []

    def set_current_selection(self, x):
        self.main.draw_box(x)
        if x != self.main.r:
            for b in self.btns:
                b.configure(state="normal")
        else:
            for b in self.btns:
                b.configure(state="disabled")

        self.widget = x
        for child in self.winfo_children():
            if child.cget("text") != self.widget.get_name():
                child.configure(fg_color=get_ui_color("neutral_800"))
            else:
                self.current_selection = child
                child.configure(fg_color=get_ui_color("primary"))

    def update_text(self, old_name, new_text):
        for child in self.winfo_children():
            if child.widget == self.widget and child.cget("text") == old_name:
                child.configure(text=new_text)

    def delete_widget(self):
        if not hasattr(self, 'widget') or self.widget is None:
            return
        self.main._parents = []
        self.main.get_parents(self.widget)
        self.main.delete_from_dict(self.main.widgets, self.main._parents, self.widget)
        self.main._parents = []

        self.widget.destroy()
        self.widget = None
        self.current_selection = None
        self.main.destroy_box()
        self.delete_children()
        self.update_list(self.main.widgets, 5)
        for btn in self.btns:
            btn.configure(state="disabled")

    def move_up(self):
        if self.current_selection != None:
            self.main.get_parents(self.widget)
            parents = self.main._parents
            siblings = self.main.get_first_degree_parent(self.main.widgets, parents)
            selection_order = self.widget.order
            sib = None
            for sibling in siblings:
                if sibling.order + 1 == selection_order:
                    sib = sibling
                    break
            if sib is not None:
                sib.order = selection_order
                self.widget.order = sib.order - 1
                self.widget.pack(**self.widget.pack_options, before=sib)
                self.main.widgets = self.main.loop_order_sort(self.main.widgets)
                self.delete_children()
                self.update_list(self.main.widgets, 5)

            self.main._parents = []
            self.current_selection = None
            self.main.destroy_box()
            self.widget = None
            for btn in self.btns:
                btn.configure(state="disabled")

    def move_down(self):
        if self.current_selection != None:
            self.main.get_parents(self.widget)
            parents = self.main._parents
            siblings = self.main.get_first_degree_parent(self.main.widgets, parents)
            selection_order = self.widget.order
            sib = None
            for sibling in siblings:
                if sibling.order - 1 == selection_order:
                    sib = sibling
                    break
            if sib is not None:
                sib.order = selection_order
                self.widget.order = sib.order + 1
                self.widget.pack(**self.widget.pack_options, after=sib)
                self.main.widgets = self.main.loop_order_sort(self.main.widgets)
                self.delete_children()
                self.update_list(self.main.widgets, 5)

            self.main._parents = []
            self.current_selection = None
            self.main.destroy_box()
            self.widget = None
            for btn in self.btns:
                btn.configure(state="disabled")

    def update_list(self, d, pad):
        try:
            self.current_selection = None
            self.widget = None
            for x in list(d.keys()):
                if d[x] != {}:
                    btn = CTkButton(self, text=x.get_name(), fg_color=get_ui_color("neutral_800"))
                    btn.configure(command=lambda x=x: (x.on_drag_start(None), self.set_current_selection(x)))
                    btn.widget = x
                    btn.pack(fill="x", padx=(pad, 5), pady=2.5)
                    self.update_list(d[x], pad+20)
                else:
                    btn = CTkButton(self, text=x.get_name(), fg_color=get_ui_color("neutral_800"))
                    btn.configure(command=lambda x=x: (x.on_drag_start(None), self.set_current_selection(x)))
                    btn.widget = x
                    btn.pack(fill="x", padx=(pad, 5), pady=2.5)
            self.main.destroy_box()
        except tkinter.TclError:
            pass

    def _change_parent(self, widget, new_parent):
        self.s = {new_parent.get_name(): {}}
        self.main._parents = []
        self.main.get_parents(new_parent)
        self.parent_parents = self.main._parents
        self.main._parents = []
        self.main.get_parents(widget)

        d = self.main.widgets.copy()
        for key in self.main._parents:
            d = d[key]

        val = d[widget]
        d = {widget: val}
        self.main._parents = []
        self.main.loop_save(d, new_parent.get_name(), self.s)
        self.s = self.s[new_parent.get_name()]
        self.main._parents = []
        self.main.get_parents(new_parent)
        self.main._parents.append(new_parent)

        self.main.loop_open(self.s, self.main._parents[-1], copy=False)
        self.main.hierarchy.delete_children()
        self.main.hierarchy.update_list(self.main.widgets, 5)
        self.main._parents = []
        self.widget = widget
        self.delete_widget()
        self.top_level.destroy()
        self.main.destroy_box()

    def get_frames_scrollbar_only(self):
        new_arr = []
        children = self.winfo_children()
        for widget in children:
            if widget.widget.__class__ in [Frame, Main, ScrollableFrame]:
                new_arr.append([widget, widget.pack_info()["padx"], widget.widget])
        return new_arr

    def set_change_parent_selection(self, x, btn):
        self.change_parent_selection = x
        self._change_parent(widget=self.widget, new_parent=self.change_parent_selection)

    def change_parent(self):
        self.top_level = CTkToplevel()
        self.top_level.geometry("500x500")
        self.top_level.title("Escolha um Parente")
        self.top_level.after(20, self.top_level.lift)
        self.scrl = CTkScrollableFrame(self.top_level)
        self.scrl.pack(fill="both", expand=True)

        arr = self.get_frames_scrollbar_only()
        for x in arr:
            btn = CTkButton(self.scrl, text=x[2].get_name(), fg_color=get_ui_color("neutral_800"))
            btn.configure(command=lambda x=x[2], btn=btn: (self.set_change_parent_selection(x, btn)))
            btn.widget = x[2]
            btn.pack(fill="x", padx=x[1], pady=2.5)

    def duplicate_widget(self):
        self.s = {self.widget.get_name(): {}}
        self.main._parents = []
        self.main.get_parents(self.widget)
        d = self.main.widgets.copy()
        for key in self.main._parents:
            d = d[key]

        val = d[self.widget]
        d = {self.widget: val}
        self.main._parents = []
        self.main.loop_save(d, self.widget.get_name(), self.s)
        self.s = self.s[self.widget.get_name()]
        self.main._parents = []
        self.main.get_parents(self.widget)
        self.main.loop_open(self.s, self.main._parents[-1], copy=True)
        self.main.hierarchy.delete_children()
        self.main.hierarchy.update_list(self.main.widgets, 5)
        self.main._parents = []

    def delete_children(self):
        for widget in self.winfo_children():
            widget.destroy()

class PaletteEditor(CTkToplevel):
    def __init__(self, *args, color_manager, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("500x500")
        self.color = get_ui_color("white")
        self.title("Paleta-de-Cores")
        self.after(20, self.lift)
        self.after(25, self.focus_get)
        self.wm_iconbitmap()
        self.iconpath = ImageTk.PhotoImage(file=resource_path('Logo.ico'))
        self.after(100, lambda: self.iconphoto(False, self.iconpath))

        self.current_selection = [None, None]
        self.clickables = []
        self.color_manager = color_manager.color_manager
        
        self.save_file = resource_path("saved_palette.json")
        self.load_saved_colors()

        self.scrl = CTkScrollableFrame(self)
        self.scrl.pack(fill="both", expand=True, padx=10, pady=(10, 0))

        self.frame2 = CTkFrame(self)
        self.frame2.pack(fill="x", padx=10, pady=(10, 5))

        self.name_entry = CTkEntry(self.frame2, placeholder_text="Digite um Nome")
        self.name_entry.pack(side="left", fill="x", expand=True, padx=(10, 0), pady=5)

        self.add_btn = CTkButton(self.frame2, text="Add", width=50, command=self.add)
        self.add_btn.pack(side="left", padx=10)

        self.fr = CTkFrame(self)
        self.fr.pack(padx=10, pady=(5, 10), fill="x")

        self.c = CTkButton(self.fr, width=100, height=100, text="", fg_color=self.color, hover=False, command=self.get_color)
        self.c.pack(side="left")

        self.hex = CTkLabel(self.fr, text=f"HEX: {self.color}", anchor="w")
        self.hex.pack(fill="x", padx=10, pady=5, expand=True)

        self.rgb = CTkLabel(self.fr, text=f"RGB: {self.hex_to_rgb(self.color)}", anchor="w")
        self.rgb.pack(fill="x", padx=10, pady=(0, 5), expand=True)

        self.change_btn = CTkButton(self.fr, text=f"Mudar", command=self.use)
        self.change_btn.pack(fill="x", padx=10, pady=(0, 10), expand=True)

        self.refresh_color_list()

    def load_saved_colors(self):
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, "r", encoding="utf-8") as f:
                    saved_colors = json.load(f)
                    for name, val in saved_colors.items():
                        self.color_manager.colors[name] = val
            except Exception as e:
                print(f"[DEBUG] Erro ao carregar paleta salva: {e}")

    def save_colors_to_file(self):
        try:
            with open(self.save_file, "w", encoding="utf-8") as f:
                json.dump(self.color_manager.colors, f, indent=4)
        except Exception as e:
            print(f"[DEBUG] Erro ao salvar paleta: {e}")

    def refresh_color_list(self):
        for x in list(self.color_manager.colors.keys()):
            self.add_color_option(x, self.color_manager.get_color(x))

    def add(self):
        name = self.name_entry.get()
        if name:
            self.color_manager.add_color(name=name, color=self.c.cget("fg_color"))
            self.add_color_option(name, self.color_manager.get_color(name))
            self.name_entry.delete(0, "end")
            self.save_colors_to_file()

    def hex_to_rgb(self, value):
        value = value.lstrip('#')
        lv = len(value)
        return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

    def select(self, name, val):
        self.current_selection = [name, val]
        self.c.configure(fg_color=self.color_manager.get_color(name))
        self.hex.configure(text=f"HEX: {self.color_manager.get_color(name)}")
        self.rgb.configure(text=f"RGB: {self.hex_to_rgb(self.color_manager.get_color(name))}")

    def add_color_option(self, name, val):
        c = CTkFrame(self.scrl, height=100)
        c.pack(fill="x", pady=10)

        clr = CTkFrame(c, width=75, height=75, fg_color=val)
        clr.pack(side="left", padx=10)

        fr = CTkFrame(c)
        fr.pack(side="left", fill="both", expand=True)

        lbl = CTkLabel(fr, text=name, anchor="w", font=CTkFont(size=17))
        lbl.pack(fill="x", expand=True, padx=10, pady=10)

        lbl2 = CTkLabel(fr, text=val, anchor="w")
        lbl2.pack(fill="x", expand=True, padx=10, pady=(0, 10))

        btn = CTkButton(c, text="X", fg_color=get_ui_color("danger"), hover_color=get_ui_color("danger_hover"), width=50, height=50)
        btn.pack(side="left", padx=10)

        for x in [c, clr, fr, lbl, lbl2]:
            x.bind("<Button-1>", lambda e, name=name, val=val: (self.select(name, val), self.change_selection([fr, c])))
        
        def delete_and_save():
            self.color_manager.delete_color(name)
            c.destroy()
            self.save_colors_file_action()

        btn.configure(command=delete_and_save)
        self.select(name, val)
        self.change_selection([fr, c])
        self.clickables.append([fr, c])

    def save_colors_file_action(self):
        self.save_colors_to_file()

    def get_color(self):
        c = askcolor(initialcolor=self.c.cget("fg_color"))
        if c != (None, None):
            self.c.configure(fg_color=c[1])

    def use(self):
        if hasattr(self, 'command') and self.command is not None:
            self.color_manager.edit(name=self.current_selection[0], val=self.c.cget("fg_color"))
            self.save_colors_to_file()
            self.destroy()

    def change_selection(self, clr):
        for x in self.clickables:
            for y in x:
                y.configure(fg_color="transparent")
        for x in clr:
            x.configure(fg_color=get_ui_color("selection"))

class WindowResizer(CTkFrame):
    def __init__(self, *args, orientation="vertical", widget=None, multiplier=1.5, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget = widget
        self.multiplier = multiplier
        self.orientation = orientation
        if widget != None:
            self.init()

    def init(self):
        self.lbl = CTkLabel(self, text="...", font=CTkFont(size=6, weight="bold"))
        self.lbl.pack(expand=True)
        if self.orientation == "vertical":
            self.configure(width=5)
            self.change_dir = "x"
            self.val = self.widget.cget("width")
            self.lbl.configure(cursor="sb_h_double_arrow", wraplength=1)
            self.bind("<Enter>", lambda e: self.winfo_toplevel().configure(cursor="sb_h_double_arrow"))
        else:
            self.configure(height=5)
            self.change_dir = "y"
            self.val = self.widget.cget("height")
            self.lbl.configure(cursor="sb_v_double_arrow", text=". . .")
            self.bind("<Enter>", lambda e: self.winfo_toplevel().configure(cursor="sb_v_double_arrow"))

        self.bind("<Button-1>", self.pressed)
        self.lbl.bind("<Button-1>", self.pressed)
        self.bind("<ButtonRelease>", self.released)
        self.lbl.bind("<ButtonRelease>", self.released)
        self.bind("<Leave>", lambda e: self.winfo_toplevel().configure(cursor="arrow"))
        self.prev = 0

    def configure(self, require_redraw=False, **kwargs):
        if "widget" in kwargs:
            self.widget = kwargs.pop("widget")
            self.init()
        super().configure(**kwargs)

    def pressed(self, e):
        self.winfo_toplevel().bind("<B1-Motion>", self.dragged)
        if self.change_dir == "x":
            self.prev = self.winfo_pointerx()
        else:
            self.prev = self.winfo_pointery()

    def dragged(self, e):
        if self.change_dir == "x":
            delta = self.winfo_pointerx() - self.prev
            delta *= self.multiplier
            self.widget.configure(width=self.val + delta)
            self.prev = self.winfo_pointerx()
            self.val += delta
        else:
            delta = self.winfo_pointery() - self.prev
            delta *= self.multiplier
            self.widget.configure(height=self.val + delta)
            self.prev = self.winfo_pointery()
            self.val += delta

    def released(self, e):
        self.winfo_toplevel().unbind("<B1-Motion>")

class App(CTkToplevel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.master:
            self.master.withdraw()
        self.geometry("1360x960+10+0")
        self.title("Custom Tkinter Builder 2.0")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.app_theme = "blue"
        self.canvas_theme = "green"
        self.after(20, self.lift)
        self.after(25, self.focus_get)

        self.after(100, lambda: (shutil.rmtree(tempify("temp"), ignore_errors=True), os.makedirs(tempify("temp"), exist_ok=True)))

        self.tool_bar = CTkFrame(self, height=40)
        self.tool_bar.pack(side="top", fill="x", padx=10, pady=(10, 0))

        self.open_btn = CTkButton(self.tool_bar, text="Abrir projeto", fg_color="transparent", width=50)
        self.open_btn.pack(side="left", padx=5, pady=5)

        self.save_btn = CTkButton(self.tool_bar, text="Salvar", fg_color="transparent", width=50)
        self.save_btn.pack(side="left", padx=5, pady=5)

        self.saveas_btn = CTkButton(self.tool_bar, text="Salvar Como", fg_color="transparent", width=50)
        self.saveas_btn.pack(side="left", padx=5, pady=5)

        self.run_code_btn = CTkButton(self.tool_bar, text="Rodar Código", fg_color="transparent", width=50)
        self.run_code_btn.pack(side="left", padx=5, pady=5)

        self.export_code_btn = CTkButton(self.tool_bar, text="Exportar Código", fg_color="transparent", width=50)
        self.export_code_btn.pack(side="left", padx=5, pady=5)

        self.palette_btn = CTkButton(self.tool_bar, text="Editar Paleta-de-Cor", fg_color="transparent", width=50)
        self.palette_btn.pack(side="left", padx=5, pady=5)

        self.assets_btn = CTkButton(self.tool_bar, text="Gerenciar Ícones", fg_color="transparent", width=50, command=lambda: AssetManagerDialog(main_app=self.main))
        self.assets_btn.pack(side="left", padx=5, pady=5)

        self.appearance_mode_switch = CTkSwitch(self.tool_bar, text="Dark Mode", border_color=get_ui_color("pair_primary"), text_color="white")
        self.appearance_mode_switch.pack(side="left", padx=5, pady=5)
        if darkdetect.isDark():
            self.appearance_mode_switch.toggle()
        self.appearance_mode_switch.configure(command=lambda: self.main.change_appearance_mode(self.appearance_mode_switch.get()))
        self.free_layout_switch = CTkSwitch(self.tool_bar, text="Modo Livre", text_color="white")
        self.free_layout_switch.pack(side="left", padx=5, pady=5)
        self.free_layout_switch.configure(command=lambda: self.main.set_layout_mode("place" if self.free_layout_switch.get() else "pack"))

        self.widget_panel = CTkTabview(self, width=250)
        self.widget_panel.pack(side=LEFT, padx=10, pady=(0, 10), fill="y")
        self.widget_panel.dragndrop_list = []
        self.widget_panel.add("Widgets Principais")
        self.widget_panel.add("Widgets com Temas")

        self.widget_panel_resizer = WindowResizer(self, orientation="vertical", widget=self.widget_panel)
        self.widget_panel_resizer.pack(side="left", fill="y")

        self.widget_panel_core_tab = self.widget_panel.tab("Widgets Principais")
        self.widget_panel_themed_tab = self.widget_panel.tab("Widgets com Temas")

        self.widget_panel_core = CTkScrollableFrame(self.widget_panel_core_tab, fg_color="transparent")
        self.widget_panel_core.pack(padx=(0, 5), pady=5, fill="both", expand=True)

        self.widget_panel_themed = CTkScrollableFrame(self.widget_panel_themed_tab, fg_color="transparent")
        self.widget_panel_themed.pack(padx=(0, 5), pady=5, fill="both", expand=True)

        self.add_frame_btn = WidgetButton(master=self.widget_panel_core, text="Frame", height=50, on_drag=lambda x, y, widget: self.main.add_widget(Frame, properties={"properties":self.properties_panel}, x=x, y=y, widget=widget))
        self.add_frame_btn.pack(padx=10, pady=(5, 0), fill="x")

        self.add_vert_scrl_frame_btn = WidgetButton(master=self.widget_panel_core, text="Vertical Scrollable Frame", height=50, on_drag=lambda x, y, widget: self.main.add_widget(ScrollableFrame, properties={"properties":self.properties_panel, "orientation": "vertical"}, x=x, y=y, widget=widget))
        self.add_vert_scrl_frame_btn.pack(padx=10, pady=(5, 0), fill="x")

        self.add_horiz_scrl_frame_btn = WidgetButton(master=self.widget_panel_core, text="Horizontal Scrollable Frame", height=50, on_drag=lambda x, y, widget: self.main.add_widget(ScrollableFrame, properties={"properties": self.properties_panel, "orientation": "horizontal"}, x=x, y=y, widget=widget))
        self.add_horiz_scrl_frame_btn.pack(padx=10, pady=(5, 0), fill="x")

        self.add_label_btn = WidgetButton(master=self.widget_panel_core, text="Label", height=50, on_drag=lambda x, y, widget: self.main.add_widget(Label, properties={"properties":self.properties_panel}, x=x, y=y, widget=widget))
        self.add_label_btn.pack(padx=10, pady=(5, 0), fill="x")

        self.add_button_btn = WidgetButton(master=self.widget_panel_core, text="Button", height=50, on_drag=lambda x, y, widget: self.main.add_widget(Button, properties={"properties":self.properties_panel}, x=x, y=y, widget=widget))
        self.add_button_btn.pack(padx=10, pady=(5, 0), fill="x")

        self.add_entry_btn = WidgetButton(master=self.widget_panel_core, text="Entry", height=50, on_drag=lambda x, y, widget: self.main.add_widget(Entry, properties={"properties":self.properties_panel}, x=x, y=y, widget=widget))
        self.add_entry_btn.pack(padx=10, pady=(5, 0), fill="x")

        self.add_switch_btn = WidgetButton(master=self.widget_panel_core, text="Switch", height=50, on_drag=lambda x, y, widget: self.main.add_widget(Switch, properties={"properties": self.properties_panel}, x=x, y=y, widget=widget))
        self.add_switch_btn.pack(padx=10, pady=(5, 0), fill="x")

        self.add_checkbox_btn = WidgetButton(master=self.widget_panel_core, text="Check Box", height=50, on_drag=lambda x, y, widget: self.main.add_widget(CheckBox, properties={"properties": self.properties_panel}, x=x, y=y, widget=widget))
        self.add_checkbox_btn.pack(padx=10, pady=(5, 0), fill="x")

        self.add_radiobutton_btn = WidgetButton(master=self.widget_panel_core, text="Radio Button", height=50, on_drag=lambda x, y, widget: self.main.add_widget(RadioButton, properties={"properties": self.properties_panel}, x=x, y=y, widget=widget))
        self.add_radiobutton_btn.pack(padx=10, pady=(5, 0), fill="x")

        self.add_horizontalslider_btn = WidgetButton(master=self.widget_panel_core, text="Horizontal Slider", height=50, on_drag=lambda x, y, widget: self.main.add_widget(Slider, properties={"properties": self.properties_panel, "orientation": "horizontal"}, x=x, y=y, widget=widget))
        self.add_horizontalslider_btn.pack(padx=10, pady=(5, 0), fill="x")

        self.add_verticalslider_btn = WidgetButton(master=self.widget_panel_core, text="Vertical Slider", height=50, on_drag=lambda x, y, widget: self.main.add_widget(Slider, properties={"properties": self.properties_panel, "orientation": "vertical"}, x=x, y=y, widget=widget))
        self.add_verticalslider_btn.pack(padx=10, pady=(5, 0), fill="x")

        self.add_combobox_btn = WidgetButton(master=self.widget_panel_core, text="Combo Box", height=50, on_drag=lambda x, y, widget: self.main.add_widget(ComboBox, properties={"properties": self.properties_panel}, x=x, y=y, widget=widget))
        self.add_combobox_btn.pack(padx=10, pady=(5, 0), fill="x")

        self.add_optionmenu_btn = WidgetButton(master=self.widget_panel_core, text="Option Menu", height=50, on_drag=lambda x, y, widget: self.main.add_widget(OptionMenu, properties={"properties": self.properties_panel}, x=x, y=y, widget=widget))
        self.add_optionmenu_btn.pack(padx=10, pady=(5, 0), fill="x")

        self.add_progressbar_btn = WidgetButton(master=self.widget_panel_core, text="Progress Bar", height=50, on_drag=lambda x, y, widget: self.main.add_widget(ProgressBar, properties={"properties": self.properties_panel}, x=x, y=y, widget=widget))
        self.add_progressbar_btn.pack(padx=10, pady=(5, 0), fill="x")

        self.add_segmentedbutton_btn = WidgetButton(master=self.widget_panel_core, text="Segmented Button", height=50, on_drag=lambda x, y, widget: self.main.add_widget(SegmentedButton, properties={"properties": self.properties_panel}, x=x, y=y, widget=widget))
        self.add_segmentedbutton_btn.pack(padx=10, pady=(5, 0), fill="x")

        self.add_textbox_btn = WidgetButton(master=self.widget_panel_core, text="TextBox", height=50, on_drag=lambda x, y, widget: self.main.add_widget(TextBox, properties={"properties": self.properties_panel}, x=x, y=y, widget=widget))
        self.add_textbox_btn.pack(padx=10, pady=(5, 0), fill="x")

        self.add_horizontalscrollbar_btn = WidgetButton(master=self.widget_panel_core, text="Horizontal Scrollbar", height=50, on_drag=lambda x, y, widget: self.main.add_widget(Scrollbar, properties={"properties": self.properties_panel, "orientation": "horizontal"}, x=x, y=y, widget=widget))
        self.add_horizontalscrollbar_btn.pack(padx=10, pady=(5, 0), fill="x")

        self.add_verticalscrollbar_btn = WidgetButton(master=self.widget_panel_core, text="Vertical Scrollbar", height=50, on_drag=lambda x, y, widget: self.main.add_widget(Scrollbar, properties={"properties": self.properties_panel, "orientation": "vertical"}, x=x, y=y, widget=widget))
        self.add_verticalscrollbar_btn.pack(padx=10, pady=(5, 0), fill="x")

        self.temp_panel = CTkFrame(self, fg_color="transparent")
        self.temp_panel.pack(side="left", pady=10, fill="both", expand=True)

        self.main_window_panel = CTkFrame(self.temp_panel, fg_color=("grey10", "grey80"))
        self.main_window_panel.pack(fill="both", expand=True, padx=5, pady=5)

        self.horiz_scrlbar = CTkSlider(master=self.temp_panel, from_=100, to=-100, number_of_steps=200, orientation="horizontal", button_length=33, width=13, border_width=12)
        self.horiz_scrlbar.configure(progress_color=self.horiz_scrlbar.master.cget("bg_color"), fg_color=self.horiz_scrlbar.master.cget("bg_color"))
        self.horiz_scrlbar.pack(fill="x", padx=10)

        self.vert_scrlbar = CTkSlider(master=self, from_=-100, to=100, number_of_steps=200, orientation="vertical", button_length=33, width=13, border_width=12)
        self.vert_scrlbar.configure(progress_color=self.vert_scrlbar.cget("bg_color"), fg_color=self.vert_scrlbar.cget("bg_color"))
        self.vert_scrlbar.pack(side="left", fill="y", padx=(10, 0), pady=10)

        t = CTkFrame(self.widget_panel_themed)
        t.pack(fill="x")
        self.add_button_1_btn = WidgetButton(master=t, text="Button 1", height=50, on_drag=lambda x, y, widget: self.main.add_widget(ThemedButton.Button_1, properties={"properties": self.properties_panel}, x=x, y=y, widget=widget))
        self.add_button_1_btn.pack(side="left", fill="x", expand=True, padx=5, pady=(10, 0))
        self.add_button_1_btn.configure(text="Button 1", width=140, height=38, corner_radius=3, fg_color=get_ui_color("themed_button_1_fg"), hover_color=get_ui_color("themed_button_1_hover"), border_color=get_ui_color("themed_button_1_border"), border_width=1, font=CTkFont(size=15, weight="normal"))

        self.add_button_2_btn = WidgetButton(master=t, text="Button 2", height=50, on_drag=lambda x, y, widget: self.main.add_widget(ThemedButton.Button_2, properties={"properties": self.properties_panel}, x=x, y=y, widget=widget))
        self.add_button_2_btn.pack(side="right", fill="x", expand=True, padx=5, pady=(10, 0))
        self.add_button_2_btn.configure(image=CTkImage(Image.open(resource_path(os.path.join("Assets", "baseline_arrow_forward_white_18dp_1x.png"))), size=(18, 18)), width=140, height=38, compound="right", text="Next", corner_radius=30, fg_color=get_ui_color("themed_button_2_fg"), text_color=get_ui_color("themed_button_2_text"), hover_color=get_ui_color("themed_button_2_hover"), border_color=get_ui_color("themed_button_2_border"), border_width=0, text_color_disabled=get_ui_color("pair_gray78_gray68"), font=CTkFont(size=15, weight="normal"))
        
        t = CTkFrame(self.widget_panel_themed)
        t.pack(fill="x")

        self.add_button_3_btn = WidgetButton(master=t, text="Button 3", height=50, on_drag=lambda x, y, widget: self.main.add_widget(ThemedButton.Button_3, properties={"properties": self.properties_panel}, x=x, y=y, widget=widget))
        self.add_button_3_btn.pack(fill="x", side="left", expand=True, pady=(10, 0), padx=(5, 0))
        self.add_button_3_btn.configure(width=140, height=38, text="Purchase", corner_radius=3, fg_color=get_ui_color("themed_button_3_fg"), text_color=get_ui_color("themed_button_3_text"), hover_color=get_ui_color("themed_button_3_hover"), border_color=get_ui_color("themed_button_3_border"), border_width=1, text_color_disabled=get_ui_color("pair_gray78_gray68"), font=CTkFont(size=15, weight="bold"))

        o = CTkFrame(t, width=self.add_button_3_btn.cget("width"), height=50, fg_color="transparent")
        o.pack(fill="x", side="right", expand=True, padx=5, pady=(10, 0))
        o.pack_propagate(False)
        self.add_icon_white_btn = WidgetButton(master=o, text="Icon White", height=50, on_drag=lambda x, y, widget: self.main.add_widget(ThemedButton.Button_Icon_white, properties={"properties": self.properties_panel}, x=x, y=y, widget=widget))
        self.add_icon_white_btn.pack(side="left", expand=True)
        self.add_icon_white_btn.configure(width=40, height=40, text="", corner_radius=3, fg_color=get_ui_color("themed_icon_white_fg"), text_color=get_ui_color("themed_icon_white_text"), hover_color=get_ui_color("themed_icon_white_hover"), border_color=get_ui_color("themed_icon_white_border"), border_width=0, text_color_disabled=get_ui_color("pair_gray78_gray68"), image=CTkImage(Image.open(resource_path(os.path.join("Assets", "baseline_people_white_18dp_1x.png"))), size=(18, 18)))

        self.add_icon_black_btn = WidgetButton(master=o, text="Icon Black", height=50, on_drag=lambda x, y, widget: self.main.add_widget(ThemedButton.Button_Icon_black, properties={"properties": self.properties_panel}, x=x, y=y, widget=widget))
        self.add_icon_black_btn.pack(side="right", expand=True)
        self.add_icon_black_btn.configure(width=40, height=40, text="", corner_radius=3, fg_color=get_ui_color("themed_icon_black_fg"), text_color=get_ui_color("themed_icon_black_text"), hover_color=get_ui_color("themed_icon_black_hover"), border_color=get_ui_color("themed_icon_black_border"), border_width=0, text_color_disabled=get_ui_color("pair_gray78_gray68"), image=CTkImage(Image.open(resource_path(os.path.join("Assets", "baseline_people_black_18dp_1x.png"))), size=(18, 18)))

        self.add_heading_1_btn = WidgetButton(master=self.widget_panel_themed, text="Heading 1", height=50, on_drag=lambda x, y, widget: self.main.add_widget(ThemedText.Heading_1, properties={"properties": self.properties_panel}, x=x, y=y, widget=widget))
        self.add_heading_1_btn.pack(padx=5, pady=(10, 0), fill="x")
        self.add_heading_1_btn.configure(text="Heading 1", font=CTkFont(size=45, weight="bold"), border_width=0)

        self.add_heading_2_btn = WidgetButton(master=self.widget_panel_themed, text="Heading 2", height=50, on_drag=lambda x, y, widget: self.main.add_widget(ThemedText.Heading_2, properties={"properties": self.properties_panel}, x=x, y=y, widget=widget))
        self.add_heading_2_btn.pack(padx=5, pady=(10, 0), fill="x")
        self.add_heading_2_btn.configure(text="Heading 2", font=CTkFont(size=45, weight="normal"), border_width=0)

        self.add_heading_3_btn = WidgetButton(master=self.widget_panel_themed, text="Sub Heading", height=50, on_drag=lambda x, y, widget: self.main.add_widget(ThemedText.SubHeading, properties={"properties": self.properties_panel}, x=x, y=y, widget=widget))
        self.add_heading_3_btn.pack(padx=5, pady=(10, 0), fill="x")
        self.add_heading_3_btn.configure(text="Sub Heading", font=CTkFont(size=30, weight="normal"), border_width=0)

        self.add_paragraph_1_btn = WidgetButton(master=self.widget_panel_themed, text="Paragraph 1", height=50, on_drag=lambda x, y, widget: self.main.add_widget(ThemedText.Paragraph_1, properties={"properties": self.properties_panel}, x=x, y=y, widget=widget))
        self.add_paragraph_1_btn.pack(padx=5, pady=(10, 0), fill="x")
        self.add_paragraph_1_btn.configure(text="I am Paragraph 1", font=CTkFont(size=15, weight="normal"), border_width=0)
        
        self.add_wrapped_paragraph_btn = WidgetButton(master=self.widget_panel_themed, text="Wrapped Paragraph", height=50, on_drag=lambda x, y, widget: self.main.add_widget(ThemedText.WrappedParagraph, properties={"properties": self.properties_panel}, x=x, y=y, widget=widget))
        self.add_wrapped_paragraph_btn.pack(padx=5, pady=(10, 0), fill="x")
        self.add_wrapped_paragraph_btn.configure(text="Lorem ipsum dolor sit amet,\n consectetur adipiscing elit,\n sed do eiusmod tempor\n incididunt ut labore et dolore\n magna aliqua.", font=CTkFont(size=15, weight="normal"), border_width=0)

        self.temp = CTkFrame(self.main_window_panel, fg_color=self.main_window_panel.cget("fg_color"))
        self.temp.pack(fill="both", expand=True, pady=10, padx=10)

        self.main_window = Main(self.temp, properties=None, width=500, height=500, bg_color=("grey10", "grey80"))
        self.main_window.pack_propagate(False)
        self.main_window.place(anchor="center", relx=0.5, rely=0.5)
        self.main_window.type = "MAIN-FRAME"
        self.main_window.num = -1
        self.main_window.name = self.main_window.type + str(self.main_window.num)

        self.drag_manager = DragManager(self.widget_panel.dragndrop_list, self.main_window, self)

        self.main = MainWindow(self.main_window, self.canvas_theme)
        self.main.drag_manager = self.drag_manager
        self.main_window.configure(fg_color=self.main.theme["CTk"]["fg_color"], bg_color=self.main_window.master.cget("fg_color")[1])

        self.hierarchy_and_properties_resizer = WindowResizer(self, orientation="vertical", multiplier=-1)
        self.hierarchy_and_properties_resizer.pack(side="left", fill="y", padx=(5, 0))
        self.container = CTkFrame(self, width=350, fg_color="transparent")
        self.container.pack(side=LEFT, padx=10, pady=10, fill="y")
        self.container.pack_propagate(False)
        self.hierarchy_and_properties_resizer.configure(widget=self.container)

        self.update()
        visible_area = self.main_window_panel.winfo_height()
        content_height = self.main_window.cget("height")
        hidden_area = (content_height - visible_area)
        offset = hidden_area//2
        offset += 50

        self.main.vert_scrl = self.vert_scrlbar
        self.vert_scrlbar.configure(command=self.main.on_vert_scrl)
        self.main_window.bind("<MouseWheel>", self.main.on_vert_mouse)
        self.temp.bind("<MouseWheel>", self.main.on_vert_mouse)
        self.main.appearance = self.appearance_mode_switch
        self.main.vert_max_offset = abs(offset)

        visible_area = self.main_window_panel.winfo_width()
        content_height = self.main_window.cget("width")
        hidden_area = (content_height - visible_area)
        offset = hidden_area // 2
        offset += 50

        self.main.horiz_scrl = self.horiz_scrlbar
        self.horiz_scrlbar.configure(command=self.main.on_horiz_scrl)
        self.main_window.bind("<Shift-MouseWheel>", self.main.on_horiz_mouse)
        self.temp.bind("<Shift-MouseWheel>", self.main.on_horiz_mouse)
        self.main.horiz_max_offset = abs(offset)

        self.hierarchy = Hierarchy(self.container, height=350)
        self.hierarchy.pack(fill="both")
        self.main.hierarchy = self.hierarchy
        self.hierarchy.main = self.main
        self.hierarchy.mainwindow = self.main_window
        self.hierarchy_tools_container = CTkFrame(self.container, height=40)
        self.hierarchy_tools_container.pack(fill="x", pady=(0, 10))

        self.move_top_btncc = CTkButton(self.hierarchy_tools_container, text="", font=("MaterialIconsOutlined-Regular", 0), width=20, height=0)
        self.move_top_btncc.pack(side="left", padx=5)

        self.move_top_btn = CTkButton(self.hierarchy_tools_container, text="⤒", font=("MaterialIconsOutlined-Regular", 20), width=20, height=20, command=self.hierarchy.move_up)
        self.move_top_btn.pack(side="left", padx=5)

        self.move_down_btn = CTkButton(self.hierarchy_tools_container, text="⤓", font=("MaterialIconsOutlined-Regular", 20), width=20, height=20, command=self.hierarchy.move_down)
        self.move_down_btn.pack(side="left", padx=5)

        self.delete_btn = CTkButton(self.hierarchy_tools_container, text="Apagar", font=("MaterialIconsOutlined-Regular", 20), width=20, height=20, command=self.hierarchy.delete_widget)
        self.delete_btn.pack(side="left", padx=5)

        self.duplicate_btn = CTkButton(self.hierarchy_tools_container, text="Duplicar", font=("MaterialIconsOutlined-Regular", 20), width=20, height=20, command=self.hierarchy.duplicate_widget)
        self.duplicate_btn.pack(side="left", padx=5)

        self.change_parent_btn = CTkButton(self.hierarchy_tools_container, text="⥃", font=("MaterialIconsOutlined-Regular", 20), width=20, height=20, command=self.hierarchy.change_parent)
        self.change_parent_btn.pack(side="left", padx=5)

        self.hierarchy.btns = [self.move_top_btn, self.move_down_btn, self.delete_btn, self.duplicate_btn, self.change_parent_btn]
        for btn in self.hierarchy.btns:
            btn.configure(state="disabled")

        self.properties_panel = PropertiesManager(self.container, main=self.main)
        self.properties_panel_resizer = WindowResizer(self.container, orientation="horizontal", multiplier=1, widget=self.hierarchy)
        self.properties_panel_resizer.pack(fill="x")

        self.main.properties = self.properties_panel
        self.properties_panel.pack(fill="both", expand=True)
        self.main_window.properties = self.properties_panel
        self.main_window.bind("<Button-1>", lambda e, nw=self.main_window: (nw.on_drag_start(None), self.hierarchy.set_current_selection(nw)))
        self.run_code_btn.configure(command=self.main.run_code)
        self.export_code_btn.configure(command=self.main.export_code)
        self.palette_btn.configure(command=lambda: self.main.show_palette(self.properties_panel))

        self.save_btn.configure(command=self.main.save_file)
        self.saveas_btn.configure(command=self.main.saveas_file)
        self.open_btn.configure(command=self.main.open_file)
        
        self.main.apply_theme_to_widget(self.main_window)
        self.wm_iconbitmap()
        self.iconpath = ImageTk.PhotoImage(file=resource_path('Logo.ico'))
        self.after(100, lambda: self.iconphoto(False, self.iconpath))

    def on_close(self):
        try:
            shutil.rmtree(tempify("temp"), ignore_errors=True)
        except Exception:
            pass
        self.destroy()
        if self.master:
            self.master.destroy()
        sys.exit(0)

class AssetManagerDialog(CTkToplevel):
    def __init__(self, *args, main_app, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_app = main_app
        self.geometry("800x450+450+200")
        self.title("Gerenciador e Banco de Ícones")
        self.after(20, self.lift)
        self.after(25, self.focus_get)
        self.wm_iconbitmap()
        self.iconpath = ImageTk.PhotoImage(file=resource_path('Logo.ico'))
        self.after(100, lambda: self.iconphoto(False, self.iconpath))

        self.tabview = CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=15, pady=15)

        self.tab_project = self.tabview.add("Assets do Projeto")
        self.tab_library = self.tabview.add("Banco de Ícones (Biblioteca)")

        self.setup_project_tab()
        self.setup_library_tab()

    def setup_project_tab(self):
        top_frame = CTkFrame(self.tab_project, fg_color="transparent")
        top_frame.pack(fill="x", padx=10, pady=10)

        lbl_title = CTkLabel(top_frame, text="Ícones vinculados a este projeto", font=CTkFont(size=16, weight="bold"))
        lbl_title.pack(side="left")

        btn_add_asset = CTkButton(top_frame, text="+ Adicionar Manualmente", width=160, command=self.add_new_asset)
        btn_add_asset.pack(side="right")

        self.scrl_project = CTkScrollableFrame(self.tab_project)
        self.scrl_project.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.load_project_assets()

    def setup_library_tab(self):
        top_lib_frame = CTkFrame(self.tab_library, fg_color="transparent")
        top_lib_frame.pack(fill="x", padx=10, pady=10)

        lbl_lib = CTkLabel(top_lib_frame, text="Biblioteca de Ícones", font=CTkFont(size=16, weight="bold"))
        lbl_lib.pack(side="left")

        self.search_entry = CTkEntry(top_lib_frame, placeholder_text="Pesquisar ícone...", width=220)
        self.search_entry.pack(side="right")
        self.search_entry.bind("<KeyRelease>", lambda e: self.filter_library_assets())

        self.scrl_library = CTkScrollableFrame(self.tab_library)
        self.scrl_library.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.library_files = []
        self.load_library_assets()

    def load_project_assets(self):
        for widget in self.scrl_project.winfo_children():
            widget.destroy()

        assets_dir = tempify("temp")
        if not os.path.exists(assets_dir):
            os.makedirs(assets_dir, exist_ok=True)

        files = [f for f in os.listdir(assets_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.ico', '.webp'))]

        if not files:
            lbl_empty = CTkLabel(self.scrl_project, text="Nenhum ícone encontrado na pasta temporária do projeto.", text_color="gray")
            lbl_empty.pack(pady=40)
            return

        row, col = 0, 0
        for file_name in files:
            file_path = os.path.join(assets_dir, file_name)
            card = CTkFrame(self.scrl_project, width=160, height=140, fg_color=get_ui_color("neutral_800"))
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            card.pack_propagate(False)

            try:
                pil_img = Image.open(file_path)
                thumb_img = CTkImage(light_image=pil_img, dark_image=pil_img, size=(48, 48))
                img_lbl = CTkLabel(card, image=thumb_img, text="")
                img_lbl.pack(pady=(12, 5))
            except Exception:
                pass

            name_lbl = CTkLabel(card, text=file_name, font=CTkFont(size=11), width=140, anchor="center")
            name_lbl.pack(padx=5, pady=(0, 5))

            del_btn = CTkButton(card, text="Excluir", fg_color=get_ui_color("danger"), hover_color=get_ui_color("danger_hover"), height=24, width=80, command=lambda fn=file_name: self.delete_asset(fn))
            del_btn.pack(pady=(0, 10))

            col += 1
            if col > 3:
                col = 0
                row += 1

    def load_library_assets(self):
        self.lib_dir = resource_path("IconLibrary")
        if not os.path.exists(self.lib_dir):
            os.makedirs(self.lib_dir, exist_ok=True)

        self.library_files = [f for f in os.listdir(self.lib_dir) if f.lower().endswith(('.png', '.ico', '.jpg'))]
        self.render_library_grid(self.library_files)

    def render_library_grid(self, files):
        for widget in self.scrl_library.winfo_children():
            widget.destroy()

        if not files:
            msg = "Nenhum ícone na pasta 'IconLibrary'.\nAdicione centenas de ícones PNG/ICO lá!"
            lbl_empty = CTkLabel(self.scrl_library, text=msg, text_color="gray", justify="center")
            lbl_empty.pack(pady=40)
            return

        row, col = 0, 0
        for file_name in files:
            file_path = os.path.join(self.lib_dir, file_name)
            card = CTkFrame(self.scrl_library, width=160, height=140, fg_color=get_ui_color("neutral_800"))
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            card.pack_propagate(False)

            try:
                pil_img = Image.open(file_path)
                thumb_img = CTkImage(light_image=pil_img, dark_image=pil_img, size=(48, 48))
                img_lbl = CTkLabel(card, image=thumb_img, text="")
                img_lbl.pack(pady=(12, 5))
            except Exception:
                pass

            clean_name = os.path.splitext(file_name)[0]
            name_lbl = CTkLabel(card, text=clean_name, font=CTkFont(size=11), width=140, anchor="center")
            name_lbl.pack(padx=5, pady=(0, 5))

            add_btn = CTkButton(card, text="Usar Ícone", height=24, width=100, command=lambda fp=file_path, fn=file_name: self.import_library_icon(fp, fn))
            add_btn.pack(pady=(0, 10))

            col += 1
            if col > 3:
                col = 0
                row += 1

    def filter_library_assets(self):
        query = self.search_entry.get().lower()
        filtered = [f for f in self.library_files if query in f.lower()]
        self.render_library_grid(filtered)

    def import_library_icon(self, src_path, file_name):
        try:
            target_temp = tempify(os.path.join("temp", file_name))
            shutil.copy2(src_path, target_temp)

            if hasattr(self.main_app, 'file') and self.main_app.file != "":
                project_assets = os.path.join(self.main_app.file[0], self.main_app.file[1], "Assets")
                if os.path.exists(project_assets):
                    shutil.copy2(src_path, project_assets)

            self.load_project_assets()
            messagebox.showinfo("Sucesso", f"Ícone '{file_name}' adicionado ao projeto!")
            self.tabview.set("Assets do Projeto")
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível importar o ícone: {e}")

    def add_new_asset(self):
        from tkinter.filedialog import askopenfilename
        filename = askopenfilename(filetypes=[("Imagens", "*.png *.jpg *.jpeg *.ico *.webp")])
        if filename:
            try:
                base_name = os.path.basename(filename)
                target_path = tempify(os.path.join("temp", base_name))
                shutil.copy2(filename, target_path)
                
                if hasattr(self.main_app, 'file') and self.main_app.file != "":
                    project_assets = os.path.join(self.main_app.file[0], self.main_app.file[1], "Assets")
                    if os.path.exists(project_assets):
                        shutil.copy2(filename, project_assets)

                self.load_project_assets()
                messagebox.showinfo("Sucesso", f"Ícone '{base_name}' adicionado com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível adicionar o ícone: {e}")

    def delete_asset(self, file_name):
        if messagebox.askyesno("Confirmar Exclusão", f"Deseja realmente remover o ícone '{file_name}'?"):
            try:
                temp_path = tempify(os.path.join("temp", file_name))
                if os.path.exists(temp_path):
                    os.remove(temp_path)

                if hasattr(self.main_app, 'file') and self.main_app.file != "":
                    project_assets = os.path.join(self.main_app.file[0], self.main_app.file[1], "Assets", file_name)
                    if os.path.exists(project_assets):
                        os.remove(project_assets)

                self.load_project_assets()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir o arquivo: {e}")

if __name__ == "__main__":
    set_default_color_theme("blue")
    app = App()
    app.mainloop()