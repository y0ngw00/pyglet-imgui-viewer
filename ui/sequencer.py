import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import imgui
import imgui.core
import pyglet

from fonts import Fonts
from sequencer_menu import SequencerMenu
from sequence import Sequence, SequenceTrack
from box_item import BoxItem
from enum_list import Boundary
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
        self.frame_bar_picked = False
        self.highlighted_color = imgui.get_color_u32_rgba(1,0.7,0,1)
        self.popup_menu = SequencerMenu(self)
        
        self.music_sequence = Sequence("Music", None, self.sequence_pos_start, self.sequence_height)
        self.formation_sequence = Sequence("Formation", None, self.sequence_pos_start, self.sequence_height)
        self.group_sequence =  Sequence("Grouping", None, self.sequence_pos_start, self.sequence_height)
        
    def render(self, x, y):
        x_scale, y_scale = imgui.get_io().display_size 
        x_pos = self.x_pos * x_scale
        y_pos = self.y_pos * y_scale
        x_size = self.x_size * x_scale
        y_size = self.y_size * y_scale
        imgui.set_next_window_position(x_pos, y_pos, imgui.ALWAYS)
        imgui.set_next_window_size(x_size, y_size, imgui.ALWAYS)

        window_flags = imgui.WINDOW_ALWAYS_HORIZONTAL_SCROLLBAR | imgui.WINDOW_ALWAYS_VERTICAL_SCROLLBAR
        if imgui.begin("Sequencer", True, flags = window_flags):           
            draw_list = imgui.get_window_draw_list()
            canvas_pos = imgui.get_window_position()  # Get the position of the canvas window
            layout_padding = [10,65]
            
            self.update_position(x = canvas_pos.x+layout_padding[0], 
                                    y = canvas_pos.y+layout_padding[1],
                                    xsize_box = imgui.get_window_width()-40, 
                                    ysize_box = imgui.get_window_height()-40)
            # self.draw_box(draw_list, color = imgui.get_color_u32_rgba(1,1,1,1), rounding = 4, thickness = 2)

            if imgui.begin_tab_bar("Sequncer Tab", imgui.TAB_BAR_FITTING_POLICY_DEFAULT):
                imgui.set_next_item_width(100)
                if imgui.begin_tab_item("Grouping&Formation").selected:
                    self.music_sequence.render(0)
                    self.formation_sequence.render(1)
                    self.group_sequence.render(2)
                    imgui.end_tab_item()

                if imgui.begin_tab_item("Motion Sequence").selected:
                    for idx, seq in enumerate(self.motion_sequences):
                        seq.render(idx)
                    imgui.end_tab_item()
                        
                imgui.end_tab_bar()
            
            # Time line
            self.draw_time_line(draw_list, -15)
                
            # Scroll bar
            imgui.set_cursor_pos((canvas_pos.x, self.sequence_height * len(self.motion_sequences) -  imgui.get_window_height()))
                
            # Draw a play line
            frame = self.parent_window.get_frame()
            frame_bar_color = imgui.get_color_u32_rgba(1,0,0,1)
            draw_list.add_line(self.x_origin+self.sequence_pos_start+frame, self.y_origin, self.x_origin+self.sequence_pos_start+frame, self.y_origin+400, imgui.get_color_u32_rgba(1,0,0,1), 2)
            draw_list.add_triangle_filled(self.x_origin+self.sequence_pos_start+frame, self.y_origin,
                                          self.x_origin+self.sequence_pos_start+frame-10, self.y_origin-10,
                                          self.x_origin+self.sequence_pos_start+frame+10, self.y_origin-10,
                                          frame_bar_color)
                
            if self.show_popup:
                self.popup_menu.render(x,y)
                
            imgui.end()
        return
    
    def draw_time_line(self, draw_list, offset):
        framerate = self.parent_window.get_framerate()
        short_line = 10
        long_line = 15
        draw_list.add_line(self.x_origin+self.sequence_pos_start, 
                                self.y_origin + offset + 25, 
                                self.x_origin+self.sequence_pos_start+3000, 
                                self.y_origin + offset + 25, imgui.get_color_u32_rgba(1,1,1,1), 1)
        for sec in range(0, 300):
            draw_list.add_text(self.x_origin+self.sequence_pos_start+sec*framerate, self.y_origin + offset, imgui.get_color_u32_rgba(1,1,1,1), "{}".format(sec))
            if sec % 5 == 0:
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
        for seq in self.motion_sequences:
            if hasattr(seq, 'target') and seq.target.is_selected():
                seq.insert_motion_track(file_path, self.parent_window.get_frame())
        self.show_popup = False
        
    def clear_all_track(self):
        for seq in self.motion_sequences:
            if hasattr(seq, 'target') and seq.target.is_selected():
                seq.clear_all_track()
        self.show_popup = False
        
    def insert_formation_keyframe(self):
        self.formation_sequence.insert_key_frame(self.parent_window.get_frame())
        for dancer in self.parent_window.get_dancers():
            dancer.add_root_keyframe(self.parent_window.get_frame())
    
    def insert_group_keyframe(self):
        self.group_sequence.insert_key_frame(self.parent_window.get_frame())
        for dancer in self.parent_window.get_dancers():
            dancer.add_group_keyframe(self.parent_window.get_frame())
            
    def insert_music_sequence(self):
        self.music_sequence.fill_sequence()
    
    def get_track_speed(self):
        if self.picked is not None and isinstance(self.picked, Sequence):
            return self.picked.get_track_speed()
        return -1
        
    def set_track_speed(self, speed):
        if self.picked is not None and isinstance(self.picked, Sequence):
            self.picked.set_track_speed(speed)
           
    def is_mouse_in_frame_bar(self,x,y)->bool:
        frame = self.parent_window.get_frame()
        if self.x_origin+self.sequence_pos_start+frame-10<=x<=self.x_origin+self.sequence_pos_start+frame+10:
            if self.y_origin-10<=y<=self.y_origin:
                return True
        return False
    
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
            if self.frame_bar_picked is True:
                self.frame_bar_picked = False

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
        
        if self.is_mouse_in_frame_bar(x,y) or self.frame_bar_picked is True:
            frame = self.parent_window.get_frame()
            self.parent_window.set_frame(frame+dx)
            self.frame_bar_picked = True
            
        for seq in self.motion_sequences:
            seq.on_mouse_drag(x,y,dx,dy)
