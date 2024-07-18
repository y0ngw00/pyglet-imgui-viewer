import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import imgui
import imgui.core
import loader

from sequencer_menu import SequencerMenu

class Sequencer:
    def __init__(self, parent_window):
        self.sequences=[]
        self.xsize_box = 1200
        self.ysize_box = 300
        
        self.x_origin = 0
        self.y_origin = 0
        
        self.sequence_pos_start = 150
        
        
        self.parent_window = parent_window
        
        self.show_popup = False
        self.picked = None
        self.popup_menu = SequencerMenu(self)      
    
    def render(self, x, y):            
        if imgui.begin("Sequencer", True):
            draw_list = imgui.get_window_draw_list()
            canvas_pos = imgui.get_cursor_screen_pos()  # Get the position of the canvas window

            layout_padding = [10,10]
            x_origin = canvas_pos.x+layout_padding[0]
            y_origin = canvas_pos.y+layout_padding[1]
            
            self.x_origin = x_origin
            self.y_origin = y_origin
            
            draw_list.add_rect(x_origin, y_origin, x_origin+self.xsize_box, y_origin+self.ysize_box, imgui.get_color_u32_rgba(1,1,1,1), rounding=4, thickness=2)

            for seq in self.sequences:
                seq.render()
                
            # Draw a play line
            frame = self.parent_window.get_frame()
            draw_list.add_line(x_origin+self.sequence_pos_start+frame, y_origin, x_origin+self.sequence_pos_start+frame, y_origin+300, imgui.get_color_u32_rgba(1,0,0,1), 2)
            draw_list.add_triangle_filled(x_origin+self.sequence_pos_start+frame, y_origin,
                                          x_origin+self.sequence_pos_start+frame-10, y_origin-10,
                                          x_origin+self.sequence_pos_start+frame+10, y_origin-10,
                                          imgui.get_color_u32_rgba(1,0,0,1))
                
            if self.show_popup:
                self.popup_menu.render(x,y)
                
            imgui.end()
        return
    
    def add_sequence(self,character):
        self.sequences.append(Sequence(character, self.sequence_pos_start))
    
    def open_motion_library(self):
        pass
    
    def insert_motion(self, file_path):
        if self.picked is not None:
            self.picked.insert_track(file_path, self.parent_window.get_frame())
    
    def is_mouse_in_sequencer(self,x,y)->bool:
        if self.x_origin<=x<=self.x_origin+self.xsize_box and self.y_origin<=y<=self.y_origin+self.ysize_box:
            return True
        return False
    
    def on_mouse_release(self, x, y, button, modifier):
        if self.is_mouse_in_sequencer(x,y):
            if button == 4:
                self.popup_menu.update_position()
                self.show_popup = True
                for seq in self.sequences:
                    if seq.is_picked(x,y):
                        self.picked = seq
                        break
        else :
            self.show_popup = False
            self.picked = None
            

            
    
class Sequence:
    def __init__(self, target,sequence_pos_start):
        self.target = target
        self.tracks=[]
        if len(target.joints) > 0 and len(target.joints[0].positions)>0:
            self.tracks.append(SequenceTrack(self, 0, len(target.joints[0].positions)))
        
        self.xsize_box = 1200
        self.ysize_box = 100
        self.x_origin = 0
        self.y_origin = 0
        
        self.padding_x = 0
        self.padding_y = 10
        self.sequence_pos_start = sequence_pos_start
        self.sequence_color = imgui.get_color_u32_rgba(1,0.7,0,1)        
    
    def render(self):
        draw_list = imgui.get_window_draw_list()
        canvas_pos = imgui.get_cursor_screen_pos()  # Get the position of the canvas window

        layout_padding = [10,10]
        self.x_origin = canvas_pos.x+self.sequence_pos_start+layout_padding[0]
        self.y_origin = canvas_pos.y+layout_padding[1]
        
        draw_list.add_rect(self.x_origin, self.y_origin+self.padding_y, 
                           self.x_origin+self.xsize_box, self.y_origin+self.ysize_box-self.padding_y, 
                           self.sequence_color, rounding=4, thickness=2)
        
        for track in self.tracks:
            track.render(self.x_origin, self.y_origin+self.padding_y, dx=1, dy = self.ysize_box-2*self.padding_y)
        
    def insert_track(self, file_path, start_frame):
        joints = loader.load_bvh_animation(file_path)
        self.target.add_animation(joints, start_frame, initialize_position= True)
        self.tracks.append(SequenceTrack(self, start_frame, len(joints[0].positions)))
                
    def is_picked(self,x,y)->bool:
        if self.x_origin<=x<=self.x_origin+self.xsize_box and self.y_origin<=y<=self.y_origin+self.ysize_box:
            return True
        return False
    
    

class SequenceTrack:
    def __init__(self, parent, start, end):
        self.frame_start = start
        self.frame_end = end
        self.parent = parent
        
        self.track_color = imgui.get_color_u32_rgba(1,1,0.7,1)
    
    def render(self, x, y, dx, dy):
        draw_list = imgui.get_window_draw_list()
        draw_list.add_rect_filled(x, y, 
                           x+dx * (self.frame_end - self.frame_start), y+dy, 
                           self.track_color, rounding=4)