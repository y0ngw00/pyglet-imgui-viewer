import imgui
import imgui.core

from sequencer_menu import SequencerMenu

class Sequencer:
    def __init__(self):
        self.sequences=[]
        self.xsize_box = 1200
        self.ysize_box = 300
        
        self.x_origin = 0
        self.y_origin = 0
        
        self.show_popup = False
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
                
            if self.show_popup:
                self.popup_menu.render(x,y)
                
            imgui.end()
            
        
        return
    
    def add_sequence(self,character):
        self.sequences.append(Sequence(character))
    
    def open_motion_library(self):
        pass
    
    def is_mouse_in_sequencer(self,x,y)->bool:
        if self.x_origin<=x<=self.x_origin+self.xsize_box and self.y_origin<=y<=self.y_origin+self.ysize_box:
            return True
        return False
    
    def on_mouse_release(self, x, y, button, modifier):
        if self.is_mouse_in_sequencer(x,y):
            if button == 4:
                self.popup_menu.update_position()
                self.show_popup = True
        else :
            self.show_popup = False
            

            
    
class Sequence:
    def __init__(self, target):
        self.target = target
        self.tracks=[]
        self.xsize_box = 1200
        self.ysize_box = 100
    
    def insert_track(self):
        pass
    
    def render(self):
        if imgui.begin("Sequencer", True):
            draw_list = imgui.get_window_draw_list()
            canvas_pos = imgui.get_cursor_screen_pos()  # Get the position of the canvas window

            layout_padding = [10,10]
            x_origin = canvas_pos.x+layout_padding[0]
            y_origin = canvas_pos.y+layout_padding[1]
            
            self.x_box = x_origin
            self.y_box = y_origin
            
            draw_list.add_rect(x_origin, y_origin, x_origin+self.xsize_box, y_origin+self.ysize_box, imgui.get_color_u32_rgba(1,1,1,1), rounding=4, thickness=2)

            imgui.end()
            
        for track in self.tracks:
            track.render()
        pass
    
    

class SequenceTrack:
    def __init__(self):
        pass
    
    
    def render(self):
        pass