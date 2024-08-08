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

import fonts
from enum_list import FileType

import loader
from ui import Dancer, KeyFrame, Sequencer, Sequence, SequenceTrack, DancerFormation, TitleBar,CustomBrowser
class UI:
    def __init__(self, window):
        imgui.create_context()
        imgui.get_io().display_size = window.width, window.height
        imgui.get_io().fonts.get_tex_data_as_rgba32()
        self.impl = create_renderer(window)
        
        fonts.initialize_imgui_fonts()
        
        imgui.new_frame()  
        imgui.end_frame()

        self.window = window
        self.scene = window.scene
        self.root = tk.Tk()
        self.root.withdraw()
        # Window variables
        self.pos_idx=0
        self.pos_idx2=0
        self.pos_list = [[0,0,0], [100,0,-50], [-100,0,-50], [200,0,0],[-200,0,0],[0,0,-100],
                         [-200,0,-100], [200,0,-100], [300,0,-50], [-300,0,50],[400,0,0],[-400,0,0]]

        self.dancers = []                   

        self.titlebar = TitleBar(self)

        self.DancerFormation = DancerFormation(self,660/2560, 0/1440, 1900/2560, 960/1440)
        self.Sequencer = Sequencer(self, 660/2560, 960/1440, 1900/2560, 480/1440)
        self.custom_browser = CustomBrowser(self,0/2560,0/1440,660/2560,1440/1440, self.scene)
                        
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
    
    def get_sequencer(self):
        return self.Sequencer
    
    def add_dancer(self, character)->None:
        self.dancers.append(Dancer(character, position_scale=1.0, radius = 30))
        self.Sequencer.add_sequence(character)
        self.scene.add_character(character)
        
    def get_character(self, idx):
        return self.scene.get_character(idx)

    def get_dancers(self):
        return self.dancers
    
    def get_num_dancers(self):
        return len(self.dancers)

    def render_file_dialog(self, file_descriptions,file_ext):
        file_types = [(file_descriptions, file_ext)]
        selected_file = filedialog.askopenfilename(filetypes=file_types)
        return selected_file
    
    def initialize_audio(self, file_path):
        self.window.initialize_audio(file_path)
        self.Sequencer.insert_music_sequence()
    
    def insert_motion(self, file_path):
        self.Sequencer.insert_motion(file_path)

    def open_file(self, file_path, file_type = FileType.Character,load_anim = True):
        ext = file_path.split('.')[-1]
        name = file_path.split('/')[-1]
        
        if file_type == FileType.Character:
            if ext == "bvh":
                character = loader.load_bvh(file_path)
                character.translate(self.pos_list[self.pos_idx])
                self.pos_idx+=1

            elif ext == "gltf" or ext == "glb":
                character = loader.load_gltf(file_path)
                character.translate(self.pos_list[self.pos_idx2])
                self.pos_idx2+=1
            
            elif ext == "fbx":
                loader.load_fbx(file_path, load_anim)
                character = loader.load_fbx(file_path, load_anim)
                character.translate(self.pos_list[self.pos_idx2])
                
                self.pos_idx2+=1
                    
            if character is not None:
                self.add_dancer(character)
        return
    
    def is_playing(self):
        return self.window.animate
    
    def get_frame(self):
        return self.window.frame
    
    def get_framerate(self):
        return self.window.framerate
    
    def get_play_time(self):
        total_seconds = self.window.frame / self.window.framerate
        minutes, seconds = divmod(total_seconds, 60)
        seconds, milliseconds = divmod(seconds, 1)
        return f"{int(minutes):02d}:{int(seconds):02d}:{int(milliseconds*1000):03d}"

    def get_fps(self):
        fps = self.window.fps
        return fps
    
    def set_frame(self, new_frame):
        self.window.set_frame = new_frame
        self.window.set_update_audio_flag(True)
    
    def on_key_press(self, symbol, modifiers) -> None:
        pass
                    
    def on_key_release(self, symbol, modifiers) -> None:
        self.DancerFormation.on_key_release(symbol, modifiers,self.window.frame)
        self.Sequencer.on_key_release(symbol, modifiers,self.window.frame)

    def on_mouse_press(self, x, y, button, modifier) -> None:
        new_y = self.window.height - y
        if button == 1:  # rotation
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
                



