import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from typing import Tuple
from pathlib import Path

import pyglet

import imgui
import imgui.core
from imgui.integrations.pyglet import create_renderer

import numpy as np
import pickle as pkl

from test import synthesize
from enum_list import FileType

class ModelConnector:
    def __init__(self, parent_window, scene):
        self.parent_window = parent_window
        self.scene = scene
        self.new_font = imgui.get_io().fonts.add_font_from_file_ttf("pyglet_render/data/PublicSans-SemiBold.ttf", 20)
        
        self.selected_audio_file = ""
        self.selected_network_file = ""
        
        
    def render(self):
        imgui.begin("Test Window")
        # clicked, value = imgui.input_text("Text Input", "")

        with imgui.font(self.new_font):
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
                selected_audio_file = self.render_file_dialog(file_descriptions, file_ext)
                # if selected_audio_file:
                #     print(f"Open File: {selected_audio_file}")
                #     self.open_file(selected_audio_file)
                self.selected_audio_file = str(selected_audio_file, FileType.Audio)
            
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
        imgui.end()

    def generate_motion(self):
        output_path = os.path.dirname(self.selected_audio_file)+"/" + self.selected_audio_file.split("/")[-1].split(".")[0] + "_output"
        traj = None
        if len(self.circles) > 0:
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
            