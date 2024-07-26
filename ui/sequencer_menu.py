import imgui
import imgui.core
import tkinter as tk
from tkinter import filedialog

import os

class SequencerMenu:
    def __init__(self, parent_window):
        self.parent_window = parent_window

        self.x_origin = 0
        self.y_origin = 0
        
        self.update = False
        self.selected = False

    
    def render(self,x,y):
        if self.update:
            imgui.core.set_next_window_position(*imgui.get_mouse_pos())
            self.update = False

        speed = self.parent_window.get_track_speed()
        
        imgui.open_popup("my_popup")
        if imgui.begin_popup_context_window("my_popup"):
            if imgui.menu_item("Insert Motion")[0]:
                self.open_motion_library()
            if imgui.menu_item("Delete Motion")[0]:
                self.parent_window.delete_motion()
            if speed>0 and imgui.begin_menu("Change Speed"):
                clicked, speed_changed = imgui.input_float("Speed", speed, 0.1)
                if clicked and speed_changed != speed and speed_changed > 0:
                    self.parent_window.set_track_speed(speed_changed)
                imgui.end_menu()

            imgui.end_popup()

    def open_motion_library(self):
        file_types = [("motion files", "*.bvh")]
        fileName = filedialog.askopenfilename(filetypes=file_types,initialdir = "./data/mixamo_library")
        if not fileName:
            return None
        if not os.path.exists(fileName):
            return None
        self.parent_window.insert_motion(fileName)

    def update_position(self):
        self.update = True
        
        return
        