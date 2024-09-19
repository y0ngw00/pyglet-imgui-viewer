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

# import fonts
from enum_list import *

import loader
from scene import SCENE
class UIInterface:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(UIInterface, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        imgui.create_context()        
        imgui.get_io().fonts.get_tex_data_as_rgba32()
        self.initialize_imgui_fonts()
        self.window = None

    def connect_renderer(self, window):
        self.impl = create_renderer(window)
        imgui.get_io().display_size = window.width, window.height
        
        imgui.new_frame()  
        imgui.end_frame()

        self.window = window
        self.root = tk.Tk()
        self.root.withdraw()
        # Window variables
        self.pos_idx2=0
        self.pos_list = [[0,0,0], [100,0,-50], [-100,0,-50], [200,0,0],[-200,0,0],[0,0,-100],
                         [-200,0,-100], [200,0,-100], [300,0,-50], [-300,0,50],[400,0,0],[-400,0,0]]

        self.dancers = []    
        
        from ui import Dancer, Sequencer, DancerFormation, TitleBar,CustomBrowser,MotionCreator
        self.titlebar = TitleBar()

        self.DancerFormation = DancerFormation(660/2560, 30/1440, 1900/2560, 960/1440)
        self.Sequencer = Sequencer(660/2560, 960/1440, 1900/2560, 480/1440)
        self.custom_browser = CustomBrowser(0/2560,30/1440,660/2560,1440/1440)
        self.motion_creator = MotionCreator(660/2560, 30/1440, 1500/2560, 1440/1440)
        
        self.impl.refresh_font_texture()

        
    def render(self):
        if self.window is None:
            return
        
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
        self.motion_creator.render()

    def is_ui_active(self):
        return imgui.is_any_item_active()
    
    def get_sequencer(self):
        return self.Sequencer
    
    def add_dancer(self, character)->None:
        bound_x, bound_z = SCENE.get_scene_bound()
        position_scale = [self.DancerFormation.xsize_box / bound_x, (self.DancerFormation.ysize_box) / bound_z ]

        from ui import Dancer
        self.dancers.append(Dancer(character, position_scale=position_scale, radius = 30))
        self.Sequencer.add_sequence(character)
        SCENE.add_character(character)
        
    def get_character(self, idx):
        return SCENE.get_character(idx)

    def get_dancers(self):
        return self.dancers
    
    def get_num_dancers(self):
        return len(self.dancers)
    
    def get_end_frame(self):
        if self.window.get_audio_framelength() == 0:
            return 150
        return int(self.window.get_audio_framelength())

    def render_open_file_dialog(self, file_descriptions,file_ext):
        file_types = [(file_descriptions, file_ext)]
        selected_file = filedialog.askopenfilename(filetypes=file_types)
        return selected_file
    
    def render_save_file_dialog(self, file_descriptions,file_ext, initial_dir = ""):
        file_types = [(file_descriptions, file_ext)]
        selected_file = filedialog.asksaveasfilename(filetypes=file_types, initialdir=initial_dir)
        return selected_file
    
    def initialize_audio(self, file_path):
        self.window.initialize_audio(file_path)
        self.Sequencer.insert_music_sequence(self.window.get_audio_framelength())
    
    def insert_motion(self, file_path, start_frame = -1):
        if start_frame == -1:
            start_frame = self.window.frame
        self.Sequencer.insert_motion(file_path, start_frame)
        
    def create_dancer(self, is_male=False):
        character = loader.create_sample_character(is_male)
        character.translate(self.pos_list[self.pos_idx2 % len(self.pos_list)])
        self.pos_idx2+=1
        self.add_dancer(character)

    def open_file(self, file_path, file_type = FileType.Character,load_anim = True):
        ext = file_path.split('.')[-1]
        name = file_path.split('/')[-1]
        
        if file_type == FileType.Character:
            if ext == "bvh":
                character = loader.load_bvh(file_path)
                character.translate(self.pos_list[self.pos_idx2])
                self.pos_idx2+=1

            elif ext == "gltf" or ext == "glb":
                character = loader.load_gltf(file_path)
                character.translate(self.pos_list[self.pos_idx2])
                self.pos_idx2+=1
            
            elif ext == "fbx":
                character = loader.load_fbx(file_path)
                character.translate(self.pos_list[self.pos_idx2])
                
                self.pos_idx2+=1
                    
            if character is not None:
                self.add_dancer(character)
        return
    
    def is_playing(self):
        return self.window.animate
    
    @property
    def formation_mode(self):
        return self.DancerFormation.mode
    
    def set_formation_mode(self, mode):
        self.DancerFormation.set_mode(mode)
    
    def show_motion_creator(self, is_show):
        self.motion_creator.show(is_show)
         
    def get_frame(self):
        return self.window.frame
    
    def get_framerate(self):
        return self.window.framerate
    
    def get_play_time(self):
        total_seconds = self.window.frame / self.window.framerate
        minutes, seconds = divmod(total_seconds, 60)
        seconds, milliseconds = divmod(seconds, 1)
        return f"{int(minutes):02d}:{int(seconds):02d}:{int(milliseconds*1000):03d}"

    def get_cam_eye(self):
        return self.window.get_cam_eye

    def get_fps(self):
        fps = self.window.fps
        return fps
    
    def set_frame(self, new_frame):
        self.window.set_frame = new_frame
        self.window.set_update_audio_flag(True)
        
    def capture_screen(self):
        self.window.capture_screen()
        
    def start_recording(self):
        self.window.start_recording()
        
    def stop_recording(self):
        self.window.stop_recording()
        
    def update_motion_library(self):
        self.custom_browser.update_motion_library()
    
    def on_key_press(self, symbol, modifiers) -> None:
        pass
                    
    def on_key_release(self, symbol, modifiers) -> None:
        self.DancerFormation.on_key_release(symbol, modifiers,self.window.frame)
        self.Sequencer.on_key_release(symbol, modifiers,self.window.frame)

    def on_mouse_press(self, x, y, button, modifier) -> None:
        new_y = self.window.height - y
        
        if self.motion_creator.is_show:
            self.motion_creator.on_mouse_press(x, new_y, button, modifier)
        else:
            if button == 1:  # rotation
                self.DancerFormation.on_mouse_press(x, new_y, button, modifier)
            self.Sequencer.on_mouse_press(x, new_y, button, modifier)

    def on_mouse_release(self, x, y, button, modifier) -> None:
        if self.motion_creator.is_show:
            self.motion_creator.on_mouse_release(x, self.window.height - y, button, modifier)
        else:
            self.DancerFormation.on_mouse_release(x, self.window.height - y, button, modifier)
            self.Sequencer.on_mouse_release(x, self.window.height - y, button, modifier)

    def on_mouse_drag(self, x, y, dx, dy, button, modifier) -> None:

        if self.motion_creator.is_show:
            self.motion_creator.on_mouse_drag(x, self.window.height - y, dx, dy)    
        else:
            self.DancerFormation.on_mouse_drag(x, self.window.height - y, dx, dy)
            self.Sequencer.on_mouse_drag(x, self.window.height - y, dx, dy)            
                
    def update_ui(self, is_animate) -> None:
        if self.window is None:
            return
        self.DancerFormation.update_ui(is_animate, self.window.frame)
        
    @classmethod
    def get_instance(cls):
        # Initialize the singleton if not already done
        if cls._instance is None:
            cls._instance = UIInterface()
        return cls._instance
    
    def initialize_imgui_fonts(self):
        self.fonts = {
            "group_idx_font": {
                "font": None,
                "path": "pyglet_render/data/PublicSans-SemiBold.ttf",
                "size": 30
            },
            "dancer_label":{
                "font": None,
                "path": "pyglet_render/data/PublicSans-SemiBold.ttf",
                "size": 15
            },
            "button_font_medium":{
                "font": None,
                "path": "pyglet_render/data/PublicSans-SemiBold.ttf",
                "size": 20
            },
            "button_font_bold":{
                "font": None,
                "path": "pyglet_render/data/PublicSans-SemiBold.ttf",
                "size": 20
            },
            "sequence_name":{
                "font": None,
                "path": "pyglet_render/data/PublicSans-SemiBold.ttf",
                "size": 20
            },
        }
        for font in self.fonts:
            self.fonts[font]["font"] = imgui.get_io().fonts.add_font_from_file_ttf(self.fonts[font]["path"], self.fonts[font]["size"])

                    

UI = UIInterface.get_instance()