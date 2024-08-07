import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import imgui
import imgui.core

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
        self.picked = None
        self.frame_bar_picked = False
        self.highlighted_color = imgui.get_color_u32_rgba(1,0.7,0,1)
        self.popup_menu = SequencerMenu(self)
        
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

        window_flags = 0
        # if self.picked is not None:
        window_flags = imgui.WINDOW_ALWAYS_HORIZONTAL_SCROLLBAR | imgui.WINDOW_ALWAYS_VERTICAL_SCROLLBAR
        if imgui.begin("Sequencer", True, flags = window_flags):           
            draw_list = imgui.get_window_draw_list()
            canvas_pos = imgui.get_window_position()  # Get the position of the canvas window
            layout_padding = [10,45]
            
            self.update_position(x = canvas_pos.x+layout_padding[0], 
                                    y = canvas_pos.y+layout_padding[1],
                                    xsize_box = imgui.get_window_width()-40, 
                                    ysize_box = imgui.get_window_height()-40)
            # self.draw_box(draw_list, color = imgui.get_color_u32_rgba(1,1,1,1), rounding = 4, thickness = 2)

            if imgui.begin_tab_bar("Sequncer Tab", imgui.TAB_BAR_FITTING_POLICY_DEFAULT):
                imgui.set_next_item_width(100)
                if imgui.begin_tab_item("Grouping&Formation").selected:
                    self.formation_sequence.render(0, False)
                    self.group_sequence.render(1, False)
                    imgui.end_tab_item()

                if imgui.begin_tab_item("Motion Sequence").selected:
                    for idx, seq in enumerate(self.motion_sequences):
                        seq.render(idx, seq==self.picked)
                    imgui.end_tab_item()
                        
                imgui.end_tab_bar()
            
                
            # Scroll bar
            imgui.set_cursor_pos((canvas_pos.x, self.sequence_height * len(self.motion_sequences) -  imgui.get_window_height()))
                
            # Draw a play line
            frame = self.parent_window.get_frame()
            frame_bar_color = imgui.get_color_u32_rgba(1,0,0,1)
            if self.picked == "frame bar":
                frame_bar_color = self.highlighted_color
            draw_list.add_line(self.x_origin+self.sequence_pos_start+frame, self.y_origin, self.x_origin+self.sequence_pos_start+frame, self.y_origin+400, imgui.get_color_u32_rgba(1,0,0,1), 2)
            draw_list.add_triangle_filled(self.x_origin+self.sequence_pos_start+frame, self.y_origin,
                                          self.x_origin+self.sequence_pos_start+frame-10, self.y_origin-10,
                                          self.x_origin+self.sequence_pos_start+frame+10, self.y_origin-10,
                                          frame_bar_color)
                
            if self.show_popup:
                self.popup_menu.render(x,y)
                
            imgui.end()
        return
    
    def add_sequence(self,character):
        seq = Sequence(character.get_name, character, self.sequence_pos_start, self.sequence_height)
        self.motion_sequences.append(seq)
        self.select(seq)
        
    def select(self, selected):
        if selected is None and hasattr(self.picked, 'target'):
            self.picked.target.select(False)
        elif hasattr(selected, 'target'): # If there is already a picked item
            selected.target.select(True)
            if self.picked is not None:
                self.picked.target.select(False)
            
        self.picked = selected
        return

    def open_motion_library(self):
        pass
    
    def delete_motion(self):
        if self.picked is not None and isinstance(self.picked, Sequence):
            self.picked.delete_motion_track()
        self.show_popup = False
    
    def insert_motion(self, file_path):
        if self.picked is not None and isinstance(self.picked, Sequence):
            self.picked.insert_motion_track(file_path, self.parent_window.get_frame())
        self.show_popup = False
    
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
    
    def on_mouse_release(self, x, y, button, modifier):
        if self.is_picked(x,y):
            for seq in self.motion_sequences:
                if seq.is_picked(x,y):
                    self.select(seq)
                    break
                
            if button == 4:
                self.popup_menu.update_position()
                self.show_popup = True
                
        else :
            self.show_popup = False
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
                seq.on_mouse_press(x,y,button,modifier)
            
    def on_mouse_drag(self, x, y, dx, dy):
        if self.show_popup:
            return
        
        if self.is_mouse_in_frame_bar(x,y) or self.frame_bar_picked is True:
            frame = self.parent_window.get_frame()
            self.parent_window.set_frame(frame+dx)
            self.frame_bar_picked = True
            
        for seq in self.motion_sequences:
            seq.on_mouse_drag(x,y,dx,dy)
