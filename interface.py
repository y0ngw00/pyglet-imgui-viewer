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
from ui import DancerCircle, KeyFrame, Sequencer, Sequence, SequenceTrack, DancerFormation, TitleBar,ModelConnector

from enum_list import FileType
class UI:
    def __init__(self, window):
        imgui.create_context()
        imgui.get_io().display_size = 1920, 1080
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


        
        self.new_pair_input = dict({"dancer1": "", "dancer2": "", "start": "", "last": ""})
        self.pairs = np.zeros([0,4], dtype = np.int32)
        
        self.new_main_input = dict({"dancer_index": "", "start": "", "last": ""})
        self.mains = np.zeros([0,3], dtype = np.int32)
        
        self.titlebar = TitleBar(self)
        self.DancerFormation = DancerFormation(self)
        self.Sequencer = Sequencer()
        self.model_connector = ModelConnector(self,self.scene)
        
        self.impl.refresh_font_texture()        

    def render(self):
    
        imgui.render()
        self.impl.render(imgui.get_draw_data())
        imgui.new_frame()

        self.titlebar.render()
        
        self.render_ui_window()

        imgui.end_frame()

    def draw_main_role_interface(self):
        if imgui.begin("Pairing", True):
            
            if imgui.begin_table("Dancer pairing", 4):  
                imgui.table_next_row()
                imgui.table_next_column()
                imgui.text("Dancer 1")
                imgui.table_next_column()
                imgui.text("Dancer 2")
                imgui.table_next_column()
                imgui.text("Start")
                imgui.table_next_column()
                imgui.text("Last")
                
                for pair_info in self.pairs:
                    imgui.table_next_row()
                    imgui.table_set_column_index(0)

                    imgui.text(str(pair_info[0]))
                    imgui.table_next_column()
                    imgui.text(str(pair_info[1]))
                    imgui.table_next_column()
                    imgui.text(str(pair_info[2]))
                    imgui.table_next_column()
                    imgui.text(str(pair_info[3]))
                
                imgui.table_next_row()
                imgui.table_set_column_index(0)
                _, self.new_pair_input["dancer1"] = imgui.input_text("##dancer1", self.new_pair_input["dancer1"])
                imgui.table_next_column()
                _, self.new_pair_input["dancer2"]= imgui.input_text("##dancer2", self.new_pair_input["dancer2"])
                imgui.table_next_column()
                _, self.new_pair_input["start"]= imgui.input_text("##first", self.new_pair_input["start"])
                imgui.table_next_column()
                _, self.new_pair_input["last"]= imgui.input_text("##last", self.new_pair_input["last"])
                imgui.table_next_column()

                imgui.end_table()
                
            if imgui.button("Add pair"):
                
                if self.new_pair_input["dancer1"]!="" and self.new_pair_input["dancer2"]!="" and self.new_pair_input["start"]!="" and self.new_pair_input["last"]!="":
                    print("Add pair")
                    print(self.new_pair_input)
                    self.pairs = np.vstack([self.pairs, [int(self.new_pair_input["dancer1"]), int(self.new_pair_input["dancer2"]), int(self.new_pair_input["start"]), int(self.new_pair_input["last"]) ]])
                    self.new_pair_input = dict({"dancer1": "", "dancer2": "", "start": "", "last": ""})
                    
            imgui.same_line()
            if imgui.button("Clear"):
                self.pairs = np.zeros([0,4], dtype = np.int32)
                self.new_pair_input = dict({"dancer1": "", "dancer2": "", "start": "", "last": ""})
                
            imgui.spacing() 
            imgui.spacing()
            imgui.spacing()  
            if imgui.begin_table("Main dancer parts", 3):  
                imgui.table_next_row()
                imgui.table_next_column()
                imgui.text("Dancer index")
                imgui.table_next_column()
                imgui.text("Start")
                imgui.table_next_column()
                imgui.text("Last")
                
                for main_info in self.mains:
                    imgui.table_next_row()
                    imgui.table_set_column_index(0)

                    imgui.text(str(main_info[0]))
                    imgui.table_next_column()
                    imgui.text(str(main_info[1]))
                    imgui.table_next_column()
                    imgui.text(str(main_info[2]))
                
                imgui.table_next_row()
                imgui.table_set_column_index(0)
                _, self.new_main_input["dancer_index"] = imgui.input_text("##dancer_index", self.new_main_input["dancer_index"])
                imgui.table_next_column()
                _, self.new_main_input["start"]= imgui.input_text("##first", self.new_main_input["start"])
                imgui.table_next_column()
                _, self.new_main_input["last"]= imgui.input_text("##last", self.new_main_input["last"])
                imgui.table_next_column()

                imgui.end_table()
                
            if imgui.button("Add Main dancer"):
                
                if self.new_main_input["dancer_index"]!="" and self.new_main_input["start"]!="" and self.new_main_input["last"]!="":
                    print("Add Main dancer part")
                    print(self.new_main_input)
                    self.mains = np.vstack([self.mains, [int(self.new_main_input["dancer_index"]), int(self.new_main_input["start"]), int(self.new_main_input["last"]) ]])
                    self.new_main_input = dict({"dancer_index": "", "start": "", "last": ""})
                    
            imgui.same_line()
            if imgui.button("Clear all parts"):
                self.mains = np.zeros([0,3], dtype = np.int32)
                self.new_main_input = dict({"dancer_index": "", "start": "", "last": ""})
                
            imgui.end()

        return
    
    def render_ui_window(self):   
        x,y = imgui.get_mouse_pos()
        
        self.DancerFormation.render(x,y)
        self.model_connector.render()
        
        self.draw_main_role_interface()
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
    

    def open_file(self, file_path):
        ext = file_path.split('.')[-1]
        name = file_path.split('/')[-1]
        if ext == "bvh":
            character = loader.load_bvh(file_path)
            character.set_position(self.pos_list[self.pos_idx])
            self.pos_idx+=1

        elif ext == "gltf" or ext == "glb":
            character = loader.load_gltf(file_path)
            character.set_position(self.pos_list[self.pos_idx2])
            self.add_dancer(character)
            self.pos_idx2+=1
        
        elif ext == "fbx":
            loader.load_fbx(file_path)
            character = loader.load_fbx(file_path)
            character.set_position(self.pos_list[self.pos_idx2])
            
            self.add_dancer(character)
            self.pos_idx2+=1
    
        if character is not None:
            self.scene.add_character(character)
        return
    
    def get_frame(self):
        return self.window.frame
    
    def on_key_press(self, symbol, modifiers) -> None:
        pass
                    
    def on_key_release(self, symbol, modifiers) -> None:
        self.DancerFormation.on_key_release(symbol, modifiers,self.window.frame)

    def on_mouse_down(self, x, y, button, modifier) -> None:
        new_y = self.window.height - y
        self.DancerFormation.on_mouse_down(x, new_y, button, modifier)


    def on_mouse_release(self, x, y, button, modifier) -> None:
        self.DancerFormation.on_mouse_release(x, self.window.height - y, button, modifier)
        self.Sequencer.on_mouse_release(x, self.window.height - y, button, modifier)

    def on_mouse_drag(self, x, y, dx, dy, button, modifier) -> None:
        self.DancerFormation.on_mouse_drag(x, self.window.height - y, dx, dy)
                
    def update_ui(self, is_animate) -> None:
        self.DancerFormation.update_ui(is_animate, self.window.frame)
                



