import sys
import os
from pathlib import Path
from datetime import datetime

CURR_PATH = os.path.dirname(os.path.abspath(__file__))
PARENT_PATH = os.path.dirname(CURR_PATH)+"/"
sys.path.insert(0, PARENT_PATH)

import pyglet
import imgui
import imgui.core
from imgui.integrations.pyglet import create_renderer

import tkinter as tk
from tkinter import filedialog

import loader

class UI:
    def __init__(self, window):
        imgui.create_context()
        imgui.get_io().display_size = 1920, 1080
        imgui.get_io().fonts.get_tex_data_as_rgba32()
        self.impl = create_renderer(window)
        
        self.new_font = imgui.get_io().fonts.add_font_from_file_ttf("model/PublicSans-SemiBold.ttf", 20)
        self.impl.refresh_font_texture()
        imgui.new_frame()  
        imgui.end_frame()

        self.window = window
        self.scene = window.scene
        self.root = tk.Tk()
        self.root.withdraw()
        # Window variables
        self.test_input = 0
        
        self.pos_idx=0
        self.pos_list = [[0,0,0], [1.5,0,-1.5], [-1.5,0,-1.5], [3.0,0,-3.0],[-3.0,0,-3.0] ]
        
        self.x_box = 0
        self.y_box = 0
        
        self.xsize_box = 300
        self.ysize_box = 300

    def render(self):
    
        imgui.render()
        self.impl.render(imgui.get_draw_data())
        imgui.new_frame()

        self.render_main_menu()
        self.render_ui_window()

        imgui.end_frame()
 
    def render_main_menu(self):
        file_ext = ""
        file_descriptions = ""
        is_open_file = False
        if imgui.begin_main_menu_bar():
            if imgui.begin_menu("File"):
                imgui.menu_item("(demo menu)", None, False, False)
                
                if imgui.menu_item("New")[0]:
                    pass
                
                if imgui.begin_menu("Open"):
                #     pass
                    if imgui.menu_item("BVH", None)[0]:
                        file_descriptions = "BVH Files"
                        file_ext = "*.bvh"
                        is_open_file = True
                    imgui.end_menu()
                imgui.separator()
                
                if imgui.begin_menu("Options"):
                    enabled = imgui.checkbox("Enabled", True)[1]
                    
                    imgui.begin_child("child", 0, 60, True)
                    for i in range(10):
                        imgui.text(f"Scrolling Text {i}")
                    imgui.end_child()
                    
                    f = imgui.slider_float("Value", 0.5, 0.0, 1.0)[1]
                    f = imgui.input_float("Input", f, 0.1)[1]
                    
                    items = ["Yes", "No", "Maybe"]
                    n = imgui.combo("Combo", 0, items)[1]
                    
                    imgui.end_menu()
                
                if imgui.menu_item("Checked", None, True)[0]:
                    pass
                
                if imgui.menu_item("Quit", "Alt+F4")[0]:
                    self.window.quit()
                
                imgui.end_menu()
            
            imgui.end_main_menu_bar()


        if is_open_file is True:
            selected_file = ""
            imgui.open_popup("Open File")

            if imgui.begin_popup_modal("Open File", None, imgui.WINDOW_ALWAYS_AUTO_RESIZE)[0]:
                selected_file = self.render_file_dialog(file_descriptions, file_ext)

            imgui.end_popup()

            if selected_file:
                print(f"Open File: {selected_file}")
                self.open_file(selected_file)

    def render_ui_window(self):   
        x,y = imgui.get_mouse_pos()
        
        imgui.begin("Test Window")
        imgui.text("This is the test window.")
        changed, self.window.frame = imgui.input_int("Animation frame", self.window.frame)

        # clicked, value = imgui.input_text("Text Input", "")

        with imgui.font(self.new_font):
            if imgui.button("Add character(bvh)"):
                file_descriptions = "3D model file(.bvh)"
                file_ext = ["*.bvh"]
                selected_character_file = self.render_file_dialog(file_descriptions, file_ext)
                if selected_character_file:
                    print(f"Open File: {selected_character_file}")
                    self.open_file(selected_character_file)

        imgui.end()

    def is_ui_active(self):
        return imgui.is_any_item_active()

    def render_file_dialog(self, file_descriptions,file_ext):
        file_types = [(file_descriptions, file_ext)]
        selected_file = filedialog.askopenfilename(filetypes=file_types)
        return selected_file
    
    def open_file(self, file_path):
        ext = file_path.split('.')[-1]
        name = file_path.split('/')[-1]
        if ext == "bvh":
            character = loader.load_bvh(file_path)
            character.set_scale([1,1,1])
        
        if character is not None:
            self.scene.add_character(character)
            self.pos_idx+=1
        return
    
    def on_key_press(self, symbol, modifiers) -> None:
        pass
                    
    def on_key_release(self, symbol, modifiers) -> None:
        pass

    def on_mouse_down(self, x, y, button, modifier) -> None:
        pass

    def on_mouse_release(self, x, y, button, modifier) -> None:
        pass

    def on_mouse_drag(self, x, y, dx, dy, button, modifier) -> None:
        pass
    
    def update_ui(self, is_animate) -> None:
        pass