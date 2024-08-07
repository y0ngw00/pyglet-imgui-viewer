import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import glob

from typing import Tuple
from pathlib import Path

import pyglet

import imgui
import imgui.core

import numpy as np
import pickle as pkl

from test import synthesize
from fonts import Fonts
from enum_list import FileType
from group_status import GroupingStatus

class CustomBrowser:
    def __init__(self, parent_window, x_pos, y_pos, x_size, y_size, scene):
        self.parent_window = parent_window
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.x_size = x_size
        self.y_size = y_size
        
        self.scene = scene
        self.button_font_bold = Fonts["button_font_bold"]["font"]
        
        self.selected_audio_file = ""
        self.selected_network_file = ""
        
        self.selected_file_idx = 0
        self.motion_library_dir = "./data/mixamo_library/"
        self.character_path = "X_Bot.fbx"
        self.grouping_status = GroupingStatus(parent_window)
        
        files = glob.glob(self.motion_library_dir + '*.fbx')
        self.motion_files = [os.path.splitext(os.path.basename(file))[0] for file in files]
        
        
    def render(self):
        x_scale, y_scale = imgui.get_io().display_size 
        x_pos = self.x_pos * x_scale
        y_pos = self.y_pos * y_scale
        x_size = self.x_size * x_scale
        y_size = self.y_size * y_scale
        imgui.set_next_window_position(x_pos, y_pos, imgui.ALWAYS)
        imgui.set_next_window_size(x_size, y_size, imgui.ALWAYS)
        
        imgui.begin("Custom Editor", flags=imgui.WINDOW_NO_MOVE)

        window_size = imgui.get_window_size()
        child_size = (window_size[0] - 30, 80/1440 * y_scale)  # 10 pixels smaller on each side
        # Begin the child window
        imgui.begin_child("Child Window1", child_size[0], child_size[1], border=False)
    
        with imgui.font(self.button_font_bold):
            if imgui.button("Create Dancer"):
                self.parent_window.open_file(self.motion_library_dir + self.character_path, FileType.Character, load_anim = False)

            imgui.same_line()

            if imgui.button("Select audio file"):
                file_descriptions = "Audio files (.wav)"
                file_ext = "*.wav"
                selected_audio_file = self.parent_window.render_file_dialog(file_descriptions, file_ext)
 
                self.selected_audio_file = str(selected_audio_file)
                self.parent_window.initialize_audio(selected_audio_file)
        
        imgui.end_child()
        imgui.separator()

        # Begin Tab bar widget
        imgui.begin_child("Child Window2", window_size[0] - 30, 880/1440*y_scale, border=True)
    
        # clicked, value = imgui.input_text("Text Input", "")
        if imgui.begin_tab_bar("Tab Browser", imgui.TAB_BAR_FITTING_POLICY_DEFAULT):
            imgui.set_next_item_width(100)
            if imgui.begin_tab_item("Grouping Status").selected:
                imgui.begin_child("Grouping widget", window_size[0] - 50, 720/1440*y_scale, border=False)
                self.grouping_status.render()
                imgui.end_child()
                
                with imgui.font(self.button_font_bold):
                    if imgui.button("Save Current Formation", width = window_size[0] - 50):
                        pass                     
                    if imgui.button("Save Current Grouping", width = window_size[0] - 50):
                        pass 
                imgui.end_tab_item()
                
            if imgui.begin_tab_item("Motion Library").selected:
                self.render_motion_library()
                imgui.end_tab_item()

            if imgui.begin_tab_item("Model Connector").selected:
                self.render_model_connector()
                imgui.end_tab_item()
                
            imgui.end_tab_bar()
        imgui.end_child()
        
        # Begin current status viewer
        imgui.begin_child("Child Window3", window_size[0] - 30, 480/1440*y_scale, border=True)        
        imgui.text("Current frame: {}".format(self.parent_window.get_frame()))
        imgui.text("Current time: {}".format(self.parent_window.get_play_time()))
        imgui.end_child()

        imgui.end()

    def render_motion_library(self):               
        # if imgui.tree_node("Checkpoint"):
            imgui.text("Number of Dancers: "+ str(self.parent_window.get_num_dancers()))
            imgui.same_line()
            if imgui.button("Create Dancer"):
                self.parent_window.open_file(self.motion_library_dir + self.character_path, FileType.Character, load_anim = False)

            imgui.text("Current: "+ self.motion_files[self.selected_file_idx])
            imgui.same_line()
            if imgui.button("Insert Motion"):
                file_path = self.motion_library_dir + self.motion_files[self.selected_file_idx] + ".fbx"
                self.parent_window.insert_motion(file_path)

            imgui.push_item_width(imgui.get_window_width() * 0.8)
            clicked, self.selected_file_idx = imgui.listbox('', self.selected_file_idx, self.motion_files, height_in_items = 30)
            imgui.pop_item_width()
        
    def render_model_connector(self):
        with imgui.font(self.button_font_bold):
            imgui.text("Current number of characters: {}".format(self.parent_window.get_num_dancers()))
            imgui.same_line()
            if imgui.button("Add character(GLTF,GLB)"):
                file_descriptions = "3D model file(.gltf, .glb)"
                file_ext = ["*.gltf","*.glb"]
                selected_character_file = "/home/imo/Downloads/Capoeira.gltf"
                # selected_character_file = self.render_file_dialog(file_descriptions, file_ext)
                # if selected_character_file:
                    # print(f"Open File: {selected_character_file}")
                self.parent_window.open_file(selected_character_file, FileType.Character)

            if imgui.button("Select audio file"):
                file_descriptions = "Audio files (.wav)"
                file_ext = "*.wav"
                selected_audio_file = self.parent_window.render_file_dialog(file_descriptions, file_ext)
                # if selected_audio_file:
                #     print(f"Open File: {selected_audio_file}")
                #     self.open_file(selected_audio_file)
                self.selected_audio_file = str(selected_audio_file)
                self.parent_window.initialize_audio(selected_audio_file)
            
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
                    self.scene.draw_trajectory(pos_traj)
                    synthesize(vel_traj,self.selected_audio_file, self.selected_network_file, output_path, endframe)
                    self.parent_window.open_file(output_path + ".bvh", FileType.Character)
            imgui.spacing()
            
            if imgui.button("Generate!"):
                self.generate_motion()

    def generate_motion(self):
        output_path = os.path.dirname(self.selected_audio_file)+"/" + self.selected_audio_file.split("/")[-1].split(".")[0] + "_output"
        traj = None
        circles = self.parent_window.get_dancers()
            for circle in self.circles:
                pos_traj,vel_traj = self.generate_trajectory(circle, 300)
                pos_traj += self.pos_list[self.pos_idx]
                self.scene.draw_trajectory(pos_traj)
                synthesize(vel_traj,self.selected_audio_file, self.selected_network_file, output_path)
                self.parent_window.open_file(output_path + ".bvh", FileType.Character)
                 
        else:
            synthesize(vel_traj,self.selected_audio_file, self.selected_network_file, output_path)   
            self.parent_window.open_file(output_path + ".bvh", FileType.Character)
        
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
            