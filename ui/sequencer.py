import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import imgui
import imgui.core
import loader

from fonts import Fonts
from sequencer_menu import SequencerMenu
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
        window_flags = imgui.WINDOW_ALWAYS_VERTICAL_SCROLLBAR
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
            self.picked.delete_track()
        self.show_popup = False
    
    def insert_motion(self, file_path):
        if self.picked is not None and isinstance(self.picked, Sequence):
            self.picked.insert_track(file_path, self.parent_window.get_frame())
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
class Sequence(BoxItem):
    def __init__(self, name, target,sequence_pos_start,sequence_height):
        super().__init__()
        self.name = name
        self.target = target
        self.children=[]

        self.padding_x = 0
        self.padding_y = 45
        self.sequence_pos_start = sequence_pos_start
        self.sequence_height = sequence_height - self.padding_y
        
        self.text_color = imgui.get_color_u32_rgba(1,1,1,1)
        self.sequence_color = imgui.get_color_u32_rgba(1,0.7,0,1)   
        self.background_color = imgui.get_color_u32_rgba(1,1,1,0.3)     

        if target is not None and len(target.joints) > 0 and len(target.joints[0].anim_layers)>0:
            for anim_layer in target.joints[0].anim_layers:
                frame_start = anim_layer.frame_original_region_start
                frame_end = anim_layer.frame_original_region_end
                self.children.append(SequenceTrack(self, target.name, frame_start, frame_end, height = self.sequence_height))
    
    def render(self, idx, is_picked):
        draw_list = imgui.get_window_draw_list()
        canvas_pos = imgui.get_window_position()  # Get the position of the canvas window
        layout_padding = [10,10]
        
        # To make scroll bar and shift the sequence following scroll.
        scroll_y = imgui.get_scroll_y()
        
        if is_picked:
            draw_list.add_rect_filled(canvas_pos.x+layout_padding[0], self.y_origin, 
                        self.x_origin+self.xsize_box, self.y_origin+self.ysize_box, 
                        self.background_color, rounding=4)
        self.update_position(x = canvas_pos.x+layout_padding[0]+self.sequence_pos_start, 
                            y = canvas_pos.y+layout_padding[1] + idx * self.sequence_height + self.padding_y - scroll_y,
                            xsize_box = imgui.get_window_width()- self.sequence_pos_start -50 , 
                            ysize_box = self.sequence_height)
        self.draw_box(draw_list, color = self.sequence_color, rounding=4, thickness=2)
        
        with imgui.font(Fonts["sequence_name"]["font"]):
            text_size = imgui.calc_text_size(self.name)
            name = self.name if self.target is None else self.target.get_name
            draw_list.add_text(canvas_pos.x + (self.sequence_pos_start-text_size.x)/2, 
                               self.y_origin + (self.sequence_height-text_size.y)/2, 
                               self.text_color, 
                               name)

        for track in self.children:
            track.render(self.x_origin, self.y_origin)
        
    def insert_track(self, file_path, start_frame):
        name, joints = loader.load_fbx_animation(file_path)
        self.target.add_animation(joints, start_frame, initialize_position= True)
        self.children.append(SequenceTrack(parent = self, 
                                           name = name, 
                                           frame_start = start_frame,
                                           frame_end = start_frame + len(joints[0].anim_layers[-1].rotations) -1,
                                           height = self.ysize_box)) 
        
    def delete_track(self):
        for idx, track in enumerate(self.children):
            if track.picked is True:
                self.target.remove_animation(idx)
                self.children.remove(track)
                break
            
        
    def get_track_speed(self):
        for idx, track in enumerate(self.children):
            if track.picked is True:
                return track.track_speed
            
        return -1
                
    def set_track_speed(self, speed):
        for idx, track in enumerate(self.children):
            if track.picked is True:
                track.track_speed = speed
                self.target.set_animation_speed(idx, speed)
                        
    def update_animation_layer(self, _track, frame_start, frame_end):
        for idx, track in enumerate(self.children):
            if track == _track:
                self.target.update_animation_layer(idx, frame_start, frame_end)
                break
            
    def translate_animation_layer(self, _track, dx):
        for idx, track in enumerate(self.children):
            if track == _track:
                self.target.translate_animation_layer(idx, dx)
                break
    
    def on_mouse_press(self, x, y, button, modifier) -> None:
        if self.is_picked(x,y):
            for track in self.children:
                track.on_mouse_press(x,y,button,modifier)
    
    def on_mouse_release(self, x, y, button, modifier):
        for track in self.children:
            track.on_mouse_release(x,y,button,modifier)
            
    def on_mouse_drag(self, x, y, dx, dy):
        for track in self.children:
            track.on_mouse_drag(x,y,dx,dy) 
    

class SequenceTrack(BoxItem):
    def __init__(self, parent, name, frame_start, frame_end, height, frame_speed = 1.0):
        super().__init__()
        self.parent = parent
        self.name = name
        self.frame_start = frame_start
        self.frame_end = frame_end
        self.frame_speed = frame_speed
        self.track_speed = 1.0
        self.height = height
        self.layout_padding = [10,10]
        
        self.track_color = imgui.get_color_u32_rgba(1,1,0.7,1)
        self.text_color = imgui.get_color_u32_rgba(0,0,0,1)
        
        self.picked = False
        self.boundary_picked= None
        self.translated = 0
    
    def render(self, x, y):        
        self.update_position(x = x + self.frame_speed * self.frame_start,
                                y = y,
                                xsize_box = self.frame_speed * (self.frame_end - self.frame_start)/self.track_speed,
                                ysize_box = self.height)
        if(self.frame_end < self.frame_start):
            self.frame_end = self.frame_start
        draw_list = imgui.get_window_draw_list()
        self.draw_box_filled(draw_list, color = self.track_color, rounding=4)
        
        if self.picked is True:
            self.draw_box(draw_list, color = imgui.get_color_u32_rgba(1,0,0,1), rounding=4, thickness=2)
        draw_list.add_text(self.x_origin+self.layout_padding[0], self.y_origin+self.layout_padding[1], self.text_color,self.name)
            
    def on_mouse_press(self, x, y, button, modifier):
        self.boundary_picked = self.is_boundary_picked(x)
        
    def on_mouse_release(self, x, y, button, modifier):
        if self.is_picked(x,y):
            self.picked = True
        else:
            self.picked = False
            
        if self.boundary_picked is not None:
            self.parent.update_animation_layer(self, self.frame_start, self.frame_end)
            self.boundary_picked = None
            
        if self.translated != 0:
            self.parent.translate_animation_layer(self, self.translated)
            self.translated = 0
            
    def on_mouse_drag(self, x, y, dx, dy):
        if self.picked is True:
            if self.boundary_picked == Boundary.Left:
                self.frame_start += dx
            elif self.boundary_picked == Boundary.Right:
                self.frame_end += dx
            else:
                self.frame_start += dx
                self.frame_end += dx   
                self.translated += dx
            
            
            
