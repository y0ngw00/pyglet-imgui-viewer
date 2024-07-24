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

        
        imgui.open_popup("my_popup")
        if imgui.begin_popup_context_window("my_popup"):
            if imgui.menu_item("Insert Motion")[0]:
                self.open_motion_library()
            if imgui.menu_item("Delete Motion")[0]:
                self.parent_window.delete_motion()

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
        