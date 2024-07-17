import sys
import os
import copy
from pathlib import Path
from typing import Tuple
from datetime import datetime

CURR_PATH = os.path.dirname(os.path.abspath(__file__))
PARENT_PATH = os.path.dirname(CURR_PATH)+"/"
sys.path.insert(0, PARENT_PATH)

import pyglet
import imgui
import imgui.core
from imgui.integrations.pyglet import create_renderer

import numpy as np
import pickle as pkl
import tkinter as tk
from tkinter import filedialog

import loader
from test import synthesize
from ui import DancerCircle, KeyFrame

class UI:
    def __init__(self, window):
        imgui.create_context()
        imgui.get_io().display_size = 1920, 1080
        imgui.get_io().fonts.get_tex_data_as_rgba32()
        self.impl = create_renderer(window)
        
        self.new_font = imgui.get_io().fonts.add_font_from_file_ttf("pyglet_render/data/PublicSans-SemiBold.ttf", 20)
        self.impl.refresh_font_texture()
        imgui.new_frame()  
        imgui.end_frame()

        self.window = window
        self.scene = window.scene
        self.root = tk.Tk()
        self.root.withdraw()
        # Window variables
        self.test_input = 0
        self.selected_audio_file = ""
        self.selected_network_file = ""
        
        self.keyframe_animate = True
        self.pos_idx=0
        self.pos_idx2=0
        self.pos_list = [[0,0,0], [100,0,-50], [-100,0,-50], [200,0,-100],[-200,0,-100],[0,0,-100] ]
        
        self.circles = []
        self.last_clicked_item = []
        
        self.x_box = 0
        self.y_box = 0
        
        self.xsize_box = 500
        self.ysize_box = 500
        
        self.new_pair_input = dict({"dancer1": "", "dancer2": "", "start": "", "last": ""})
        self.pairs = np.zeros([0,4], dtype = np.int32)
        
        self.new_main_input = dict({"dancer_index": "", "start": "", "last": ""})
        self.mains = np.zeros([0,3], dtype = np.int32)

    def render(self):
    
        imgui.render()
        self.impl.render(imgui.get_draw_data())
        imgui.new_frame()

        self.render_main_menu()
        self.render_ui_window()

        imgui.end_frame()
        
    def draw_formation_interface(self, x, y):
        if imgui.begin("Drawing Interface", True, flags=imgui.WINDOW_NO_MOVE):
            draw_list = imgui.get_window_draw_list()
            canvas_pos = imgui.get_cursor_screen_pos()  # Get the position of the canvas window

            layout_padding = [10,10]
            x_origin = canvas_pos.x+layout_padding[0]
            y_origin = canvas_pos.y+layout_padding[1]
            
            self.x_box = x_origin
            self.y_box = y_origin
            
            draw_list.add_rect(x_origin, y_origin, x_origin+self.xsize_box, y_origin+self.ysize_box, imgui.get_color_u32_rgba(1,0,0,1), rounding=5, thickness=3)
            
            frame = self.window.frame
            
            main_dancer_color = imgui.get_color_u32_rgba(0,1,0,1)
            main_dancers = []
            for main_info in self.mains:
                if frame < main_info[2] and frame >= main_info[1]:
                    main_dancers.append(self.circles[main_info[0]])

            # Draw a dot
            for circle in self.circles:
                color =  imgui.get_color_u32_rgba(1,1,1,1)
                
                if len(circle.sync_keyframe.keyframes) > 1:
                    left, right = circle.sync_keyframe.get_nearest_keyframe(frame)
                    if left %2 ==0 and right %2 ==1:
                        color = imgui.get_color_u32_rgba(1,0.7,0,1)
                        
                if circle in main_dancers:
                    color = main_dancer_color
                
                if circle in self.last_clicked_item and self.window.animate is False:
                    color = imgui.get_color_u32_rgba(1,1,0,1)
                    
                draw_list.add_circle_filled(x_origin+circle.x, y_origin+circle.y, circle.radius,color)

            imgui.end()
        return
    
    def draw_keyframe_interface(self):
        if imgui.begin("Keyframe editor", True):
            draw_list = imgui.get_window_draw_list()
            canvas_pos = imgui.get_cursor_screen_pos()  # Get the position of the canvas window

            changed, self.window.frame = imgui.slider_float("Frame", self.window.frame, 0.0, self.window.max_frame)
            imgui.same_line()
            check_clicked, bAnimate = imgui.checkbox("Animate", self.keyframe_animate)
            if check_clicked is True:
                self.keyframe_animate = bAnimate
            slider_pos = (canvas_pos.x + 10, canvas_pos.y + 40)

            for idx, circle in enumerate(self.circles):
                imgui.text("Dancer '{}'".format(idx))
                canvas_x, canvas_y= copy.deepcopy(imgui.get_cursor_screen_pos())
                canvas_x += 80
                
                draw_list.add_rect(canvas_x, canvas_y, canvas_x+300, canvas_y+20, imgui.get_color_u32_rgba(1,1,1,1), rounding=5, thickness=3)
                for idx, keyframe in enumerate(circle.pose_keyframe.keyframes):
                    x = canvas_x +  self.xsize_box * keyframe.frame / self.window.max_frame
                    
                    if idx > 0 and keyframe.position != circle.pose_keyframe.keyframes[idx-1].position:
                        prev_x = canvas_x +  self.xsize_box * circle.pose_keyframe.keyframes[idx-1].frame / self.window.max_frame
                        draw_list.add_rect_filled(prev_x, canvas_y, x, canvas_y+20, imgui.get_color_u32_rgba(0.7, 0, 0, 1))
                    else:
                        draw_list.add_line(x, canvas_y, x, canvas_y+20, imgui.get_color_u32_rgba(0.7, 0, 0, 1))
                        
                imgui.text("trajectory")

                canvas_y += 30
                draw_list.add_rect(canvas_x, canvas_y, canvas_x+300, canvas_y+20, imgui.get_color_u32_rgba(1,1,1,1), rounding=5, thickness=3)
                for idx, keyframe in enumerate(circle.sync_keyframe.keyframes):
                    x = canvas_x +  self.xsize_box * keyframe.frame / self.window.max_frame
                    
                    if idx > 0 and idx %2 ==1:
                        prev_x = canvas_x +  self.xsize_box * circle.sync_keyframe.keyframes[idx-1].frame / self.window.max_frame
                        draw_list.add_rect_filled(prev_x, canvas_y, x, canvas_y+20, imgui.get_color_u32_rgba(1, 0.6, 0, 1))
                    else:
                        draw_list.add_line(x, canvas_y, x, canvas_y+20, imgui.get_color_u32_rgba(1, 0.6, 0, 1))
                imgui.spacing() 
                imgui.spacing()
                imgui.spacing()
                imgui.text("synchronize")
                
                canvas_pos = imgui.get_cursor_pos()
                imgui.set_cursor_pos((10, canvas_pos.y+40))
            
            imgui.end()
            
            if changed:
                self.update_ui(self.keyframe_animate)
        return

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

                    if imgui.menu_item("GLTF", None)[0]:
                        file_descriptions = "GLTF Files"
                        file_ext = ["*.gltf","*.glb"]
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
        
        self.draw_formation_interface(x,y)
        
        self.draw_keyframe_interface()
        
        self.draw_main_role_interface()

        imgui.begin("Test Window")
        imgui.text("This is the test window.")
        changed, self.window.frame = imgui.input_int("Animation frame", self.window.frame)

        # clicked, value = imgui.input_text("Text Input", "")

        with imgui.font(self.new_font):
            imgui.text("Current number of characters: {}".format(len(self.circles)))
            imgui.same_line()
            if imgui.button("Add character(GLTF,GLB)"):
                file_descriptions = "3D model file(.gltf, .glb)"
                file_ext = ["*.gltf","*.glb"]
                selected_character_file = "/home/imo/Downloads/Capoeira.gltf"
                # selected_character_file = self.render_file_dialog(file_descriptions, file_ext)
                # if selected_character_file:
                    # print(f"Open File: {selected_character_file}")
                self.open_file(selected_character_file)

            if imgui.button("Select audio file"):
                file_descriptions = "Audio files (.wav)"
                file_ext = "*.wav"
                selected_audio_file = self.render_file_dialog(file_descriptions, file_ext)
                # if selected_audio_file:
                #     print(f"Open File: {selected_audio_file}")
                #     self.open_file(selected_audio_file)
                self.selected_audio_file = str(selected_audio_file)
            
            imgui.text(self.selected_audio_file)
            imgui.spacing()
            
            if imgui.button("Select model checkpoint"):
                file_descriptions = "checkpoint file (.ckpt)"
                file_ext = "*.ckpt"
                self.selected_network_file = self.render_file_dialog(file_descriptions, file_ext)
            imgui.text(self.selected_network_file)
            imgui.spacing()
            
            if imgui.button("Draw random trajectoris from gcd"):
                data_root = "./data/gdance/"
                path = "train_split_sequence_names.txt"
                pos_traj_list, vel_traj_list = self.generate_random_trajectory_from_gcd(data_root, path)
                idx=0
                endframe = pos_traj_list.shape[1]
                for pos_traj,vel_traj in zip(pos_traj_list, vel_traj_list):
                    output_path = "/home/imo/Downloads/gcd_output_" + str(idx)
                    idx+=1 
                    
                    # pos_traj += self.pos_list[self.pos_idx]
                    self.window.draw_trajectory(pos_traj)
                    synthesize(vel_traj,self.selected_audio_file, self.selected_network_file, output_path, endframe)
                    self.open_file(output_path + ".bvh")
            imgui.spacing()
            
            if imgui.button("Generate!"):
                self.generate_motion()
        imgui.end()

    def is_ui_active(self):
        return imgui.is_any_item_active()
    
    def generate_motion(self):
        output_path = os.path.dirname(self.selected_audio_file)+"/" + self.selected_audio_file.split("/")[-1].split(".")[0] + "_output"
        traj = None
        if len(self.circles) > 0:
            for circle in self.circles:
                pos_traj,vel_traj = self.generate_trajectory(circle, 300)
                pos_traj += self.pos_list[self.pos_idx]
                self.window.draw_trajectory(pos_traj)
                synthesize(vel_traj,self.selected_audio_file, self.selected_network_file, output_path)
                self.open_file(output_path + ".bvh")
                 
        else:
            synthesize(vel_traj,self.selected_audio_file, self.selected_network_file, output_path)   
            self.open_file(output_path + ".bvh")
        
    def generate_trajectory(self, circle, nframe: int) -> Tuple[np.ndarray, np.ndarray]:
        pos_traj = np.zeros([nframe,3], dtype = np.float32)
        vel_traj = np.zeros([nframe,3], dtype = np.float32)
        for i in range(nframe):
            circle.animate(i)
            pos_traj[i] = circle.get_character_pos()
            
            vel_traj[i,0] = pos_traj[i,0] - pos_traj[i-1,0] if i>0 else 0
            vel_traj[i,1] = pos_traj[i,2] - pos_traj[i-1,2] if i>0 else 0
            vel_traj[i,2] = 0
            
        return pos_traj,vel_traj
    
    def generate_random_trajectory_from_gcd(self, data_root, path) -> Tuple[np.ndarray, np.ndarray]:
        with open(data_root+path, encoding='utf-8') as f:
            files = [f.rstrip() for f in f.readlines()]
        
        random_idx = np.random.randint(0, len(files))
        fname = files[random_idx]
  
        if fname == "":
            print("No file at line: " + str(fname))
            return
        
        #Load motion files
        pose_dir = Path(data_root) / f"motions_smpl/{fname}.pkl"
        with open(pose_dir, "rb") as f:
            seq_data = pkl.load(f)
        
        smpl_poses = seq_data["smpl_poses"] #shape (n_persons, n_frames, pose_dim) , smpl pose excluding L/R hand joint
        if smpl_poses.shape[-1]<23*3:
            smpl_poses = np.concatenate([smpl_poses, np.zeros(list(smpl_poses.shape[:-1]) + [23*3 -smpl_poses.shape[-1] ])], axis=-1)
        if "smpl_orients" in seq_data:
            smpl_orients = seq_data["smpl_orients"]
            smpl_poses = np.concatenate([smpl_orients, smpl_poses], axis=-1)            
        smpl_trans = seq_data["root_trans"]
        
        num_persons,num_frame,_ = smpl_trans.shape
        
        pos_traj = np.zeros([num_persons,num_frame,3], dtype = np.float32)
        vel_traj = np.zeros([num_persons,num_frame,3], dtype = np.float32)
        
        pos_traj = smpl_trans
        vel_traj[:,1:] = pos_traj[:,1:] - pos_traj[:,:-1]
        
        vel_traj[:,:,1] = vel_traj[:,:,2]
        vel_traj[:,:,2] = 0
        
        return pos_traj,vel_traj
            

    def render_file_dialog(self, file_descriptions,file_ext):
        file_types = [(file_descriptions, file_ext)]
        selected_file = filedialog.askopenfilename(filetypes=file_types)
        return selected_file
    
    def is_in_formation_box(self, x, y) -> bool:
        if self.x_box<=x<=self.x_box+self.xsize_box and self.y_box<=(self.window.height - y)<=self.y_box+self.ysize_box:
            return True
        return False
    
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
            
            self.circles.append(DancerCircle(character,self.xsize_box, self.ysize_box, 1))
            self.pos_idx2+=1
        
        if character is not None:
            self.scene.add_character(character)
        return
    
    def on_key_press(self, symbol, modifiers) -> None:
        pass
                    
    def on_key_release(self, symbol, modifiers) -> None:
        if symbol == pyglet.window.key.F:
            if modifiers == pyglet.window.key.MOD_CTRL:
                for circle in self.circles:
                    circle.add_keyframe(KeyFrame(self.window.frame, (circle.x, circle.y)))
            else:
                if len(self.last_clicked_item) >0:
                    for circle in self.last_clicked_item:
                        circle.add_keyframe(KeyFrame(self.window.frame, (circle.x, circle.y)))
                    
        if symbol == pyglet.window.key.G:
            if modifiers == pyglet.window.key.MOD_CTRL:
                for circle in self.circles:
                    circle.add_sync_keyframe(KeyFrame(self.window.frame, (circle.x, circle.y)))
            else:
                if len(self.last_clicked_item) >0:
                    for circle in self.last_clicked_item:
                        circle.add_sync_keyframe(KeyFrame(self.window.frame, (circle.x, circle.y)))
        
        dx = 5 if symbol==pyglet.window.key.D else -5 if symbol==pyglet.window.key.A else 0
        dy = 5 if symbol==pyglet.window.key.S else -5 if symbol==pyglet.window.key.W else 0
        if len(self.last_clicked_item) >0:
            for circle in self.last_clicked_item:
                circle.translate(dx, dy)

    def on_mouse_down(self, x, y, button, modifier) -> None:
        new_y = self.window.height - y
        for circle in self.circles:
            if (x-self.x_box-circle.x)**2 + (new_y - self.y_box-circle.y)**2 < circle.radius**2:
                circle.set_is_clicked = True
            else:
                circle.set_is_clicked = False


    def on_mouse_release(self, x, y, button, modifier) -> None:
        for circle in self.circles:
            if circle.get_is_clicked:
                if modifier is not pyglet.window.key.MOD_SHIFT and modifier != 17:
                    self.last_clicked_item = []
                self.last_clicked_item.append(circle)
            circle.set_is_clicked = False
            
        if self.is_ui_active() is False:
            self.last_clicked_item = []

    def on_mouse_drag(self, x, y, dx, dy, button, modifier) -> None:
        if self.is_in_formation_box(x, y):
            for circle in self.last_clicked_item:
                circle.translate(dx, -dy)
                
    def update_ui(self, is_animate) -> None:
        
        if is_animate:
            for circle in self.circles:
                circle.animate(self.window.frame)
                



