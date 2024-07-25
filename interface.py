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

import numpy as np
import tkinter as tk
from tkinter import filedialog

import loader
from ui import DancerCircle, KeyFrame, Sequencer, Sequence, SequenceTrack, DancerFormation, TitleBar,CustomBrowser

from enum_list import FileType
class UI:
    def __init__(self, window):
        imgui.create_context()
        imgui.get_io().display_size = window.width, window.height
        imgui.get_io().fonts.get_tex_data_as_rgba32()
        self.impl = create_renderer(window)
        
        
        imgui.new_frame()  
        imgui.end_frame()

        self.window = window
        self.scene = window.scene
        self.root = tk.Tk()
        self.root.withdraw()
        # Window variables
        self.pos_idx=0
        self.pos_idx2=0
        self.pos_list = [[0,0,0], [100,0,-50], [-100,0,-50], [200,0,-100],[-200,0,-100],[0,0,-100] ]

        self.titlebar = TitleBar(self)
        self.DancerFormation = DancerFormation(self)
        self.Sequencer = Sequencer(self)
        self.custom_browser = CustomBrowser(self,self.scene)
        
        self.impl.refresh_font_texture()
        
    def render(self):
    
        imgui.render()
        self.impl.render(imgui.get_draw_data())
        imgui.new_frame()

        self.titlebar.render()
        
        self.render_ui_window()

        imgui.end_frame()
    
    def render_ui_window(self):   
        x,y = imgui.get_mouse_pos()
        
        self.DancerFormation.render(x,y)
        self.custom_browser.render()
        self.Sequencer.render(x,self.window.height - y)

    def is_ui_active(self):
        return imgui.is_any_item_active()
    
    def add_dancer(self, character)->None:
        self.DancerFormation.add_dancer(character)
        self.Sequencer.add_sequence(character)

    
    def get_num_dancers(self):
        return self.DancerFormation.get_num_dancers()

    def render_file_dialog(self, file_descriptions,file_ext):
        file_types = [(file_descriptions, file_ext)]
        selected_file = filedialog.askopenfilename(filetypes=file_types)
        return selected_file
    
    def initialize_audio(self, file_path):
        self.window.initialize_audio(file_path)
    
    def insert_motion(self, file_path):
        self.Sequencer.insert_motion(file_path)

    def open_file(self, file_path, file_type = FileType.Character,load_anim = True):
        ext = file_path.split('.')[-1]
        name = file_path.split('/')[-1]
        
        if file_type == FileType.Character:
            if ext == "bvh":
                character = loader.load_bvh(file_path)
                character.translate(self.pos_list[self.pos_idx])
                self.add_dancer(character)
                self.pos_idx+=1

            elif ext == "gltf" or ext == "glb":
                character = loader.load_gltf(file_path)
                character.translate(self.pos_list[self.pos_idx2])
                self.add_dancer(character)
                self.pos_idx2+=1
            
            elif ext == "fbx":
                loader.load_fbx(file_path, load_anim)
                character = loader.load_fbx(file_path, load_anim)
                character.translate(self.pos_list[self.pos_idx2])
                
                if character.joints is not None:
                    self.add_dancer(character)
                self.pos_idx2+=1
                    
            if character is not None:
                self.scene.add_character(character)
        return
    
    def is_playing(self):
        return self.window.animate
    
    def get_frame(self):
        return self.window.frame
    
    def set_frame(self, new_frame):
        self.window.set_frame = new_frame
        self.window.set_update_audio_flag(True)
    
    def on_key_press(self, symbol, modifiers) -> None:
        pass
                    
    def on_key_release(self, symbol, modifiers) -> None:
        self.DancerFormation.on_key_release(symbol, modifiers,self.window.frame)

    def on_mouse_press(self, x, y, button, modifier) -> None:
        new_y = self.window.height - y
        self.DancerFormation.on_mouse_press(x, new_y, button, modifier)
        self.Sequencer.on_mouse_press(x, new_y, button, modifier)

    def on_mouse_release(self, x, y, button, modifier) -> None:
        self.DancerFormation.on_mouse_release(x, self.window.height - y, button, modifier)
        self.Sequencer.on_mouse_release(x, self.window.height - y, button, modifier)

    def on_mouse_drag(self, x, y, dx, dy, button, modifier) -> None:
        self.DancerFormation.on_mouse_drag(x, self.window.height - y, dx, dy)
        self.Sequencer.on_mouse_drag(x, self.window.height - y, dx, dy)
                
    def update_ui(self, is_animate) -> None:
        self.DancerFormation.update_ui(is_animate, self.window.frame)
                



