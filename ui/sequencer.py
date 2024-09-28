import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import imgui
import imgui.core
import pyglet
import numpy as np

from sequencer_menu import SequencerMenu
from sequence import Sequence
from frame_bar import FrameBar
from box_item import BoxItem
from enum_list import Boundary, MotionPart

import loader

from ops import CollisionHandler, SocialForceModel

from interface import UI

class Sequencer(BoxItem):
    def __init__(self, x_pos, y_pos, x_size, y_size):
        super().__init__()
        self.motion_sequences=[]
        self.sequence_pos_start = 150
        self.sequence_height = 110
        
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.x_size = x_size
        self.y_size = y_size
        
        self.show_popup = False
        self.selected_elements = []
        self.highlighted_color = imgui.get_color_u32_rgba(1,0.7,0,1)
        self.popup_menu = SequencerMenu(self)
        
        self.frame_bar = FrameBar(self, length = 400,
                                  x_offset= self.sequence_pos_start, 
                                  y_offset = 0, 
                                  color = imgui.get_color_u32_rgba(1,0,0,1))
        
        self.music_sequence = Sequence("Music", None, self.sequence_pos_start, self.sequence_height)
        self.formation_sequence = Sequence("Formation", None, self.sequence_pos_start, self.sequence_height)
        self.pose_sequence = Sequence("Pose", None, self.sequence_pos_start, self.sequence_height)
        self.group_sequence =  Sequence("Grouping", None, self.sequence_pos_start, self.sequence_height)
    
    def load(self):
        pass
            
    def render(self, x, y):
        x_scale, y_scale = imgui.get_io().display_size 
        x_pos = self.x_pos * x_scale
        y_pos = self.y_pos * y_scale
        x_size = self.x_size * x_scale
        y_size = self.y_size * y_scale
        frame = UI.get_frame()
        imgui.set_next_window_position(x_pos, y_pos, imgui.ALWAYS)
        imgui.set_next_window_size(x_size, y_size, imgui.ALWAYS)

        window_flags = imgui.WINDOW_ALWAYS_HORIZONTAL_SCROLLBAR | imgui.WINDOW_ALWAYS_VERTICAL_SCROLLBAR
        if imgui.begin("Sequencer", True, flags = window_flags):           
            draw_list = imgui.get_window_draw_list()
            canvas_pos = imgui.get_window_position()  # Get the position of the canvas window
            layout_padding = [10,65]
            
            # To make scroll bar and shift the sequence following scroll.
            scroll_x = imgui.get_scroll_x()
            # Separator between label and sequences
            draw_list.add_line(canvas_pos.x+layout_padding[0]+self.sequence_pos_start, 
                               canvas_pos.y+layout_padding[1] + 10, 
                               canvas_pos.x+layout_padding[0]+self.sequence_pos_start, 
                               canvas_pos.y+1500, 
                               imgui.get_color_u32_rgba(1,1,1,1), 2)

            self.update_position(x = canvas_pos.x+layout_padding[0] - scroll_x, 
                                    y = canvas_pos.y+layout_padding[1],
                                    xsize_box = imgui.get_window_width()-40 + scroll_x, 
                                    ysize_box = imgui.get_window_height()-40)
            # self.draw_box(draw_list, color = imgui.get_color_u32_rgba(1,1,1,1), rounding = 4, thickness = 2)

            if imgui.begin_tab_bar("Sequncer Tab", imgui.TAB_BAR_FITTING_POLICY_DEFAULT):
                imgui.set_next_item_width(100)
                if imgui.begin_tab_item("Grouping&Formation").selected:
                    self.music_sequence.render(0, frame)
                    self.formation_sequence.render(1,frame)
                    self.pose_sequence.render(2,frame)
                    self.group_sequence.render(3,frame)
                    imgui.end_tab_item()

                if imgui.begin_tab_item("Motion Sequence").selected:
                    for idx, seq in enumerate(self.motion_sequences):
                        seq.render(idx, frame)
                    imgui.end_tab_item()
                        
                imgui.end_tab_bar()
            
            # Time line
            self.draw_time_line(draw_list, -15)
                
            # Draw a play line
            self.frame_bar.update_position(self.x_origin + self.sequence_pos_start, self.y_origin)
            self.frame_bar.render(draw_list, frame)
                
            if self.show_popup:
                self.popup_menu.render(x,y)
            
            # Scroll bar
            imgui.set_cursor_pos((self.x_origin+self.xsize_box+2*frame, self.sequence_height * len(self.motion_sequences) -  imgui.get_window_height()))
                    
            imgui.end()
        return
    
    def draw_time_line(self, draw_list, offset):
        framerate = UI.get_framerate()
        short_line = 10
        long_line = 15
        draw_list.add_line(self.x_origin, 
                                self.y_origin + offset + 25, 
                                self.x_origin+self.sequence_pos_start+9000, 
                                self.y_origin + offset + 25, imgui.get_color_u32_rgba(1,1,1,1), 1)
        for sec in range(0, 300):
            if sec % 5 == 0:
                draw_list.add_text(self.x_origin+self.sequence_pos_start+sec*framerate, self.y_origin + offset, imgui.get_color_u32_rgba(1,1,1,1), "{}".format(sec))
                draw_list.add_line(self.x_origin+self.sequence_pos_start+sec*framerate, 
                                self.y_origin + offset + 25, 
                                self.x_origin+self.sequence_pos_start+sec*framerate, 
                                self.y_origin + offset + short_line, imgui.get_color_u32_rgba(1,1,1,1), 1)
            else :
                draw_list.add_line(self.x_origin+self.sequence_pos_start+sec*framerate, 
                                self.y_origin + offset + 25, 
                                self.x_origin+self.sequence_pos_start+sec*framerate, 
                                self.y_origin + offset + long_line, imgui.get_color_u32_rgba(1,1,1,1), 1)

    
    def add_sequence(self,character):
        seq = Sequence(character.get_name, character, self.sequence_pos_start, self.sequence_height)
        self.motion_sequences.append(seq)
        self.select(seq)
        
    def select(self, selected, modifier = None):
        if selected != "frame bar" and modifier is imgui.KEY_MOD_SHIFT: # Multi-select
            if selected in self.selected_elements:
                self.selected_elements.remove(selected)
                if hasattr(selected, 'target'):
                    selected.target.select(False)
            else:
                self.selected_elements.append(selected)
                if hasattr(selected, 'target'):
                    selected.target.select(True) 
        else: # Single select
            for elem in self.selected_elements:
                if hasattr(elem, 'target'):
                    elem.target.select(False)
            if hasattr(selected, 'target'):
                    selected.target.select(True)        
                
            self.selected_elements = [selected]

        return

    def open_motion_library(self):
        pass
    
    def delete_motion(self):
        for seq in self.motion_sequences:
            if hasattr(seq, 'target') and seq.target.is_selected():
                seq.delete_motion_track()
        self.show_popup = False
        
    def mirror_motion(self):
        for seq in self.motion_sequences:
            if hasattr(seq, 'target') and seq.target.is_selected():
                seq.mirror_motion()
        self.show_popup = False
        
    def update_motion_sequence(self):
        # Used only when load a .csp file. Create motion sequences from the loaded characters' animation
        # Problem: Cannot load the name of each motion track.
        for seq in self.motion_sequences:
            if hasattr(seq, 'target'):
                for i, anim in enumerate(seq.target.root.anim_layer):
                    seq.insert_track(str(i), anim.frame_play_region_start, anim.frame_play_region_end)
    
    def insert_motion(self, file_path, load_translation, start_frame, motion_part = MotionPart.FULL):
        for idx, seq in enumerate(self.motion_sequences):
            if hasattr(seq, 'target') and seq.target.is_selected():
                loader.load_pose_from_pkl(file_path, seq.target, 0, frame = start_frame, use_translation=load_translation, load_part = motion_part)
                name = file_path.split('/')[-1]
                sequence_length = seq.target.root.anim_layer[-1].animation_length
                seq.insert_track(name, start_frame, start_frame + sequence_length -1)
        self.show_popup = False
        
    def clear_all_track(self):
        for seq in self.motion_sequences:
            if hasattr(seq, 'target') and seq.target.is_selected():
                seq.clear_all_track()
        self.show_popup = False
          
    def insert_formation_track(self,formation, prev_frame, curr_frame):
        self.formation_sequence.insert_track("Form " + str(len(self.formation_sequence.children)), prev_frame, curr_frame, formation)
    
    def insert_grouping_track(self, frame):
        self.group_sequence.insert_key_frame(frame)
    
    def insert_music_sequence(self, duration):
        self.music_sequence.fill_sequence(0, duration)
    
    def get_track_speed(self):
        for seq in self.motion_sequences:
            if hasattr(seq, 'target') and seq.target.is_selected():
                return seq.get_track_speed()
        
    def set_track_speed(self, speed):
        for seq in self.motion_sequences:
            if hasattr(seq, 'target') and seq.target.is_selected():
                return seq.set_track_speed(speed)
            
    # def keyframe_post_processing(self, curr_frame):
    #     num_dancers = len(UI.get_dancers())
    #     if num_dancers == 0:
    #         return
    #     keyframes = np.zeros((num_dancers, 2), dtype = np.int32)
    #     for i, dancer in enumerate(UI.get_dancers()):
    #         f_1, f_2 = dancer.root_keyframe.get_nearest_keyframe(curr_frame)
    #         keyframes[i] = [f_1, f_2]
            
    #     min_frame = np.min(keyframes[:,0])
    #     max_frame = np.max(keyframes[:,1])
        
    #     if min_frame == max_frame:
    #         return
        
    #     col_handler = CollisionHandler(radius = 10, n_knot = 1)
    #     col_handler.handle_collision(UI.get_dancers(), min_frame, max_frame)
        
    def on_key_release(self, symbol, modifiers, frame):
        if symbol==pyglet.window.key.P and modifiers==pyglet.window.key.MOD_CTRL:
            self.formation_sequence.clear_all_track()
            self.pose_sequence.clear_all_track
            self.group_sequence.clear_all_track()
            UI.formation_controller.clear()     
            UI.grouping_controller.clear()
                
    def on_mouse_release(self, x, y, button, modifier):
        if self.is_picked(x,y):
            if button == 4:
                self.show_popup = True                
                self.popup_menu.update_position()                
        else :
            self.show_popup = False
            if self.frame_bar.selected is True:
                self.frame_bar.select(False)

        if self.show_popup and button != 4:
            return
        
        self.formation_sequence.on_mouse_release(x,y,button,modifier)
        for seq in self.motion_sequences:
            seq.on_mouse_release(x,y,button,modifier)
            
    def on_mouse_press(self, x, y, button, modifier) -> None:
        if self.show_popup:
            return
        
        if self.is_picked(x,y):
            self.formation_sequence.on_mouse_press(x,y,button,modifier)
            for seq in self.motion_sequences:
                if seq.is_picked(x,y):
                    seq.on_mouse_press(x,y,button,modifier)
                    self.select(seq,modifier)
                    break

    def on_mouse_drag(self, x, y, dx, dy):
        if self.show_popup:
            return
        
        frame = UI.get_frame()
        if self.frame_bar.is_picked(x,y) or self.frame_bar.selected is True:
            UI.set_frame(frame+dx)
            self.frame_bar.select(True)
        
        else:
            self.formation_sequence.on_mouse_drag(x,y,dx,dy)
            for seq in self.motion_sequences:
                seq.on_mouse_drag(x,y,dx,dy)
