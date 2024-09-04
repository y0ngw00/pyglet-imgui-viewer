import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import glob
import subprocess

from typing import Tuple
from pathlib import Path

import pyglet

import imgui
import imgui.core

import numpy as np
import pickle as pkl

import loader

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
        self.status_font = Fonts["dancer_label"]["font"]   
        
        self.selected_audio_file = ""
        self.selected_network_file = ""
        
        self.selected_file_idx = 0
        self.output_dir = "./results/"
        self.motion_library_dir = "./data/smpl/"
        # self.default_character_path = "idle.fbx"
        self.default_character_path = "./data/SMPL_m_unityDoubleBlends_lbs_10_scale5_207_v1.0.0.fbx"

        self.grouping_status = GroupingStatus(parent_window)
        
        self.motion_files = []
        self.is_no_inpaint = False
        self.update_motion_library()
        
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
                self.parent_window.create_dancer()

            imgui.same_line()

            if imgui.button("Select audio file"):
                file_descriptions = "Audio files (.wav)"
                file_ext = ["*.wav", "*.m4a"]
                selected_audio_file = self.parent_window.render_open_file_dialog(file_descriptions, file_ext)
 
                self.selected_audio_file = str(selected_audio_file)
                self.parent_window.initialize_audio(selected_audio_file)
        
        imgui.text("Number of Dancers: "+ str(self.parent_window.get_num_dancers()))

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
                        self.save_current_formation()                     
                    if imgui.button("Save Current Grouping", width = window_size[0] - 50):
                        self.save_current_grouping()
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
        imgui.begin_child("Child Window3", window_size[0] - 30, 400/1440*y_scale, border=True)        
        with imgui.font(self.status_font):
            imgui.text("Current frame: {}".format(self.parent_window.get_frame()))
            imgui.text("Current time: {}".format(self.parent_window.get_play_time()))
            imgui.text("Current FPS: {:02f}".format(self.parent_window.get_fps()))
        imgui.end_child()

        imgui.end()
        
    def save_current_formation(self):
        self.parent_window.get_sequencer().insert_formation_keyframe()
        return
        
    def save_current_grouping(self):
        self.parent_window.get_sequencer().insert_group_keyframe()
        return

    def render_motion_library(self):
        current_motion = ""    
        if len(self.motion_files) > 0:
            current_motion = self.motion_files[self.selected_file_idx]

        # imgui.text("Current: "+ current_motion)
        # imgui.same_line()
        if imgui.button("Insert Motion"):
            file_path = self.motion_library_dir + current_motion + ".fbx"
            self.parent_window.insert_motion(file_path)
        imgui.same_line()
        if imgui.button("Refresh"):
            self.update_motion_library()
        imgui.same_line()
        if imgui.button("Load Folder"):
            subprocess.run(['xdg-open', self.motion_library_dir])


        window_size = imgui.get_window_size()
        imgui.push_item_width(window_size[0] * 0.8)
        clicked, self.selected_file_idx = imgui.listbox('', self.selected_file_idx, self.motion_files, height_in_items = 25)
        imgui.pop_item_width()

        with imgui.font(self.button_font_bold):
            if imgui.button("Insert Current Motion", width = window_size[0] - 50):
                file_path = self.motion_library_dir +current_motion + ".fbx"
                self.parent_window.insert_motion(file_path)
            if imgui.button("Create New Motion", width = window_size[0] - 50):
                self.parent_window.show_motion_creator(True)
                        
    def render_model_connector(self):
        with imgui.font(self.button_font_bold):
            imgui.text("Current number of characters: {}".format(self.parent_window.get_num_dancers()))
            imgui.same_line()
            if imgui.button("Add character(GLTF,GLB)"):
                file_descriptions = "3D model file(.gltf, .glb)"
                file_ext = ["*.gltf","*.glb"]
                selected_character_file = "/home/imo/Downloads/Capoeira.gltf"
                # selected_character_file = self.render_open_file_dialog(file_descriptions, file_ext)
                # if selected_character_file:
                    # print(f"Open File: {selected_character_file}")
                self.parent_window.open_file(selected_character_file, FileType.Character)

            if imgui.button("Select audio features"):
                file_descriptions = "Audio features (.npy)"
                file_ext = ["*.npy"]
                selected_audio_file = self.parent_window.render_open_file_dialog(file_descriptions, file_ext)
                # if selected_audio_file:
                #     print(f"Open File: {selected_audio_file}")
                #     self.open_file(selected_audio_file)
                self.selected_audio_file = str(selected_audio_file)
            
            imgui.text(self.selected_audio_file)
            imgui.spacing()
            
            if imgui.button("Select model checkpoint"):
                file_descriptions = "checkpoint file (.ckpt)"
                file_ext = "*.ckpt"
                self.selected_network_file = self.parent_window.render_open_file_dialog(file_descriptions, file_ext)
            imgui.text(self.selected_network_file)
            imgui.spacing()
            
            
            frmae = self.parent_window.get_end_frame()
            if imgui.button("Generate!"):
                # self.load_smpl_motion()
                self.generate_motion(frmae)
            imgui.same_line()
            _, self.is_no_inpaint = imgui.checkbox("All Random", self.is_no_inpaint)
                
            if imgui.button("Debug generate!"):
                file_descriptions = "Motion file (.pkl)"
                file_ext = ["*.pkl"]
                motion_path = self.parent_window.render_open_file_dialog(file_descriptions, file_ext)
                self.load_smpl_motion(motion_path)
                
    def update_motion_library(self):
        files = glob.glob(self.motion_library_dir + '*.fbx')
        self.motion_files = [os.path.splitext(os.path.basename(file))[0] for file in files]
        

    def generate_motion(self, nframe):
        output_path = os.path.dirname(self.output_dir)+"/"
        traj = None
        circles = self.parent_window.get_dancers()
        for circle in circles:
            circle.target.clear_all_animation()           
            motion_cond = None if self.is_no_inpaint else circle.get_motion_condition(nframe)
            loader.generate_motion_from_network(circle.target, motion_cond, self.selected_audio_file, self.selected_network_file, output_path, nframe)
            # self.parent_window.insert_motion(output_path, 0)
                 
        # else:
        #     rot_traj = self.extract_rotations(nframe)
        #     condition={"rot_traj":rot_traj}
        #     synthesize(vel_traj,self.selected_audio_file, self.selected_network_file, output_path)   
        #     self.parent_window.open_file(output_path + ".bvh", FileType.Character)
        
    def load_smpl_motion(self,motion_path):
        # path = "./data/test/-4yoUMiBwXg_01_0_960.pkl"
        # path = "./results/0_0_val_val.pkl"
        circles = self.parent_window.get_dancers()
        for idx, circle in enumerate(circles):
            circle.target.clear_all_animation()
            loader.load_pose_from_pkl(motion_path, circle.target, idx, use_translation=False)
   
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
    
    def extract_root_positions(self, circle, nframe: int) -> Tuple[np.ndarray, np.ndarray]:
        pos_traj = np.zeros([nframe,3], dtype = np.float32)
        vel_traj = np.zeros([nframe,3], dtype = np.float32)
        
        for i in range(nframe):
            character = circle.target
            character.animate(i)
        
            pos_traj[i] = circle.get_character_pos()
            
            vel_traj[i,0] = pos_traj[i,0] - pos_traj[i-1,0] if i>0 else 0
            vel_traj[i,1] = pos_traj[i,2] - pos_traj[i-1,2] if i>0 else 0
            vel_traj[i,2] = 0
            
        return pos_traj,vel_traj
    
    def extract_rotations(self, circle, nframe: int) -> np.ndarray:
        num_joints = character = self.parent_window.get_character(0).get_num_joints()
        rotations = np.zeros([nframe, num_joints * 3], dtype = np.float32)
        
        for f in range(nframe):
            character = circle.target
            character.animate(f)
            rotations[f,:] = character.get_rotation(f).flatten()
        return rotations
    
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
            