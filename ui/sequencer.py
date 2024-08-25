import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import imgui
import imgui.core
import pyglet
import numpy as np

from fonts import Fonts
from sequencer_menu import SequencerMenu
from sequence import Sequence, SequenceTrack
from frame_bar import FrameBar
from box_item import BoxItem
from enum_list import Boundary

import loader

from ops import CollisionHandler
class Sequencer(BoxItem):
    def __init__(self, parent_window, x_pos, y_pos, x_size, y_size):
        super().__init__()
        self.motion_sequences=[]
        self.sequence_pos_start = 150
        self.sequence_height = 110
        
        self.parent_window = parent_window
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
        self.group_sequence =  Sequence("Grouping", None, self.sequence_pos_start, self.sequence_height)
        
    def render(self, x, y):
        x_scale, y_scale = imgui.get_io().display_size 
        x_pos = self.x_pos * x_scale
        y_pos = self.y_pos * y_scale
        x_size = self.x_size * x_scale
        y_size = self.y_size * y_scale
        frame = self.parent_window.get_frame()
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
                    self.group_sequence.render(2,frame)
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
        framerate = self.parent_window.get_framerate()
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
    
    def insert_motion(self, file_path):
        name, joints = loader.load_fbx_animation(file_path)
        for seq in self.motion_sequences:
            if hasattr(seq, 'target') and seq.target.is_selected():
                seq.insert_motion_track(name, joints, self.parent_window.get_frame())
        self.show_popup = False
    
    def insert_smpl_motion(self, idx, data):
        seq = self.motion_sequences[idx]
        if hasattr(seq, 'target') and seq.target.is_selected():
            seq.insert_smpl_motion_track(data, self.parent_window.get_frame())
        
    def clear_all_track(self):
        for seq in self.motion_sequences:
            if hasattr(seq, 'target') and seq.target.is_selected():
                seq.clear_all_track()
        self.show_popup = False
        
    def insert_formation_keyframe(self):
        curr_frame = self.parent_window.get_frame()
        self.formation_sequence.insert_key_frame(curr_frame)
        for dancer in self.parent_window.get_dancers():
            dancer.add_root_keyframe(curr_frame)
            
        self.keyframe_post_processing(curr_frame)
    
    def insert_group_keyframe(self):
        self.group_sequence.insert_key_frame(self.parent_window.get_frame())
        for dancer in self.parent_window.get_dancers():
            dancer.add_group_keyframe(self.parent_window.get_frame())
            
    def insert_music_sequence(self):
        self.music_sequence.fill_sequence()
    
    def get_track_speed(self):
        for seq in self.motion_sequences:
            if hasattr(seq, 'target') and seq.target.is_selected():
                return seq.get_track_speed()
        
    def set_track_speed(self, speed):
        for seq in self.motion_sequences:
            if hasattr(seq, 'target') and seq.target.is_selected():
                return seq.set_track_speed(speed)
            
    def keyframe_post_processing(self, curr_frame):
        keyframes = np.zeros((len(self.parent_window.get_dancers()), 2), dtype = np.int32)
        for i, dancer in enumerate(self.parent_window.get_dancers()):
            f_1, f_2 = dancer.root_keyframe.get_nearest_keyframe(curr_frame)
            keyframes[i] = [f_1, f_2]
            
        min_frame = np.min(keyframes[:,0])
        max_frame = np.max(keyframes[:,1])
        
        if min_frame == max_frame:
            return
        
        col_handler = CollisionHandler(radius = 10, n_knot = 1)
        col_handler.handle_collision(self.parent_window.get_dancers(), min_frame, max_frame)
        
    def on_key_release(self, symbol, modifiers, frame):
        if symbol==pyglet.window.key.P:
            self.formation_sequence.clear_all_track()
            self.group_sequence.clear_all_track()
            for dancer in self.parent_window.get_dancers():
                dancer.clear_root_keyframe()
                dancer.clear_group_keyframe()
                
    def on_mouse_release(self, x, y, button, modifier):
        self.show_popup = False
        if self.is_picked(x,y):                
            if button == 4:
                self.popup_menu.update_position()
                self.show_popup = True                
        else :
            if self.frame_bar.selected is True:
                self.frame_bar.select(False)

        if self.show_popup and button != 4:
            return
          
        for seq in self.motion_sequences:
            seq.on_mouse_release(x,y,button,modifier)
            
    def on_mouse_press(self, x, y, button, modifier) -> None:
        if self.show_popup:
            return        
        if self.is_picked(x,y):
            for seq in self.motion_sequences:
                if seq.is_picked(x,y):
                    seq.on_mouse_press(x,y,button,modifier)
                    self.select(seq,modifier)
                    break
            
    def on_mouse_drag(self, x, y, dx, dy):
        if self.show_popup:
            return
        
        frame = self.parent_window.get_frame()
        if self.frame_bar.is_picked(x,y) or self.frame_bar.selected is True:
            self.parent_window.set_frame(frame+dx)
            self.frame_bar.select(True)
            
        for seq in self.motion_sequences:
            seq.on_mouse_drag(x,y,dx,dy)
