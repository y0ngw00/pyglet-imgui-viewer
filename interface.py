import sys
import os
from pathlib import Path
from datetime import datetime

CURR_PATH = os.path.dirname(os.path.abspath(__file__))
PARENT_PATH = os.path.dirname(CURR_PATH)+"/"
sys.path.insert(0, PARENT_PATH)

import glob 
import pickle as pkl
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
        self.reset()
        self.impl.refresh_font_texture()
        
    def reset(self):
        self.root = tk.Tk()
        self.root.withdraw()
        # Window variables
        self.pos_idx2=0
        self.pos_list = [[0,0,0], [50,0,-50], [-50,0,-50], [100,0,0],[-100,0,0],[0,0,-100],
                         [-100,0,-100], [100,0,-100], [150,0,-50], [-150,0,50],[200,0,0],[-200,0,0]]

        self.dancers = []    
        
        from ui import Dancer, Sequencer, DancerFormation, TitleBar,CustomBrowser,MotionCreator
        from ui import FormationController, GroupingController

        self.titlebar = TitleBar()

        self.DancerFormation = DancerFormation(660/2560, 30/1440, 1900/2560, 960/1440)
        self.Sequencer = Sequencer(660/2560, 960/1440, 1900/2560, 480/1440)
        self.custom_browser = CustomBrowser(0/2560,30/1440,660/2560,1440/1440)
        self.motion_creator = MotionCreator(660/2560, 30/1440, 1500/2560, 1440/1440)
        self.formation_controller = FormationController()
        self.grouping_controller = GroupingController()

        
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
        
    def new_project(self):
        self.reset()
        SCENE.clear_scene()
        
    def load_project(self):
        file_descriptions = "ChoreoStudio Project File"
        file_ext = "*.csp"
        selected_file = UI.render_open_file_dialog(file_descriptions, file_ext)
        
        if not selected_file or not os.path.exists(selected_file):
            print(f"File not found: {selected_file}")
            return
        
        self.new_project()
        with open(selected_file, 'rb') as f:
            data = pkl.load(f)
            
            SCENE.load_project(data)        

            ui_data = data["interface"]
            if "grouping_controller" in ui_data:
                self.grouping_controller.load(ui_data["grouping_controller"])
            if "formation_controller" in ui_data:
                self.formation_controller.load(ui_data["formation_controller"])
            # for item in ui_data.items():
            #     component = item[1]
            #     if hasattr(component, "save"):
            #         component.save(item[0], data)
            # self.__dict__.update(data["interface"])
            
        self.synchronize_scene()
        
    def save_project(self):
        file_descriptions = "ChoreoStudio Project File"
        file_ext = "*.csp"
        selected_file = UI.render_save_file_dialog(file_descriptions, file_ext)
        if not selected_file:
            return
        
        with open(selected_file, 'wb') as f:
            # pkl.dump(self.__dict__, f)
            data = {}
            SCENE.save_project(data)
            
            ui_data = {}
            state = self.__dict__.copy()
            exclude_list = ["impl", "root", "window", "fonts", "dancers","pos_list","pos_idx2"]
            for key in exclude_list:
                if key in state:
                    del state[key]
                    
            for item in state.items():
                component = item[1]
                if hasattr(component, "save"):
                    component.save(item[0], ui_data)

            data["interface"] = ui_data
            
            f.write(pkl.dumps(data))
            
    def synchronize_scene(self):
        
        self.Sequencer.update_motion_sequence()
        
        for form in self.formation_controller.get_all_formation():
            formation_shift = self.formation_controller.get_formation_shift_animation(form)
            start_frame = formation_shift.frame_play_region_start
            end_frame = formation_shift.frame_play_region_end
            self.Sequencer.insert_formation_track(formation_shift, start_frame, end_frame)

        for group in self.grouping_controller.get_all_grouping():
            self.Sequencer.insert_grouping_track(group.frame)
            
    def is_ui_active(self):
        return imgui.is_any_item_active()
    
    def get_sequencer(self):
        return self.Sequencer

    def adjust_formation_layout(self, layout_mode = LayoutMode.FULL):
        x_pos = 660/2560 if layout_mode == LayoutMode.FULL else 660/2560
        y_pos = 30/1440
        xsize = 1900/2560 if layout_mode == LayoutMode.FULL else 950/2560
        ysize = 960/1440
        self.DancerFormation.update_layout(x_pos, y_pos, xsize, ysize)
    
    def add_dancer(self, character)->None:
        bound_x, bound_z = SCENE.get_scene_bound()
        position_scale = [self.DancerFormation.xsize_box / bound_x, (self.DancerFormation.ysize_box) / bound_z ]

        from ui import Dancer
        self.dancers.append(Dancer(character, position_scale=position_scale, radius = 20))
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
    
    def insert_motion(self, file_path, load_translation, start_frame = -1):
        if start_frame == -1:
            start_frame = self.window.frame
        self.Sequencer.insert_motion(file_path, load_translation, start_frame)
        
    def insert_formation(self):
        curr_frame = UI.get_frame()
        prev_frame = max(0, curr_frame-30)
        if curr_frame < 0 :
            return
        
        dancers = UI.get_dancers()
        dancer_positions = [dancer.get_character_pos().copy() for dancer in dancers]
        formation_boundaries = self.DancerFormation.get_boundary_points()
        
        self.formation_controller.insert_formation_keyframe(dancers, dancer_positions, formation_boundaries, prev_frame, curr_frame)
        curr_formation = self.formation_controller.get_closest_formation(curr_frame)
        formation_shift = self.formation_controller.get_formation_shift_animation(curr_formation)
        self.Sequencer.insert_formation_track(formation_shift, prev_frame, curr_frame)
        
        
    
    def insert_grouping(self):
        curr_frame = self.get_frame()
        dancers = self.get_dancers()
        group_indices = np.array([dancer.group_index for dancer in dancers], dtype = np.int8)
        
        self.grouping_controller.insert_grouping_keyframe(dancers, curr_frame, group_indices)
        
        curr_group = self.grouping_controller.get_closest_grouping(curr_frame)
        self.Sequencer.insert_grouping_track(curr_frame)
            
    def create_dancer(self, is_male=False):
        character = loader.create_sample_character(is_male)
        
        position = self.pos_list[self.pos_idx2 % len(self.pos_list)] if self.pos_idx2 < len(self.pos_list) else np.random.randint(-500,500,3)
        position[1] = 0
        character.translate(position)
        self.pos_idx2+=1
        self.add_dancer(character)

    def open_file(self, file_path, file_type = FileType.Character,load_anim = True, texture_path = ""):
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
        if symbol == pyglet.window.key.SLASH and modifiers ==pyglet.window.key.MOD_ALT:
            self.debug_action()
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
        
        if is_animate:
            self.formation_controller.animate(self.window.frame)
            self.grouping_controller.animate(self.window.frame)

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
                "size": 20
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

    def debug_action(self):
        # circle = self.dancers[0]
        # files = glob.glob("data/smpl/*.fbx")
        # for file in files:
        #     UI.insert_motion(file, True)
            
        #     motion_path = file[:-4] + ".pkl" 
        #     loader.save_pkl(motion_path, circle.target, circle.target.root.anim_layer[0].animation_length)
        #     circle.target.clear_all_animation()
        
        # files = glob.glob("data/smpl/hps_track_1.npy")
        # for file in files:
        #     UI.insert_motion(file, True)
        
        # file = "data/smpl/hps_track_1.npy"
        # motion_path = file[:-4] + ".pkl" 
        # loader.convert_npy_to_pkl(file,"data/smpl/camera.npy", motion_path)
        
        #     loader.save_pkl(motion_path, circle.target, circle.target.root.anim_layer[0].animation_length)
        #     circle.target.clear_all_animation()
        pass
UI = UIInterface.get_instance()