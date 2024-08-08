
import imgui
import imgui.core
import loader

from fonts import Fonts
from box_item import BoxItem
from enum_list import Boundary

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
                self.children.append(SequenceTrack(self, target.name, frame_start, frame_end))
    
    def render(self, idx):
        draw_list = imgui.get_window_draw_list()
        canvas_pos = imgui.get_window_position()  # Get the position of the canvas window
        layout_padding = [10,10]
        
        # To make scroll bar and shift the sequence following scroll.
        scroll_y = imgui.get_scroll_y()
        
        if self.target is not None and self.target.is_selected():
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
        
    def insert_motion_track(self, file_path, start_frame):
        name, joints = loader.load_fbx_animation(file_path)
        self.target.add_animation(joints, start_frame, initialize_position= True)
        self.children.append(SequenceTrack(parent = self, 
                                           name = name, 
                                           frame_start = start_frame,
                                           frame_end = start_frame + len(joints[0].anim_layers[-1].rotations) -1,
                                           )) 
        
    def insert_key_frame(self, frame):
        self.children.append(SequenceTrack(parent = self, 
                                           frame_start = frame,
                                           frame_end = frame + 1,
                                           )) 
        
    def fill_sequence(self, start=0, end=None):
        if end is None:
            end = self.xsize_box
        self.children.append(SequenceTrack(parent = self, 
                                           name = "Music",
                                           frame_start = start,
                                           frame_end = end,
                                           )) 
        
    def delete_motion_track(self):
        for idx, track in enumerate(self.children):
            if track.selected is True:
                self.target.remove_animation(idx)
                self.children.remove(track)
                break
    
    def clear_all_track(self):
        self.children.clear()
        if self.target is not None:
            self.target.clear_all_animation()
            
    def get_track_speed(self):
        for idx, track in enumerate(self.children):
            if track.selected is True:
                return track.track_speed
            
        return -1
                
    def set_track_speed(self, speed):
        for idx, track in enumerate(self.children):
            if track.selected is True:
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
    def __init__(self, parent, name="", frame_start=0, frame_end=0, frame_speed = 1.0):
        super().__init__()
        self.parent = parent
        self.name = name
        self.frame_start = frame_start
        self.frame_end = frame_end
        self.frame_speed = frame_speed
        self.track_speed = 1.0
        self.height = parent.ysize_box
        self.layout_padding = [10,10]
        
        self.track_color = imgui.get_color_u32_rgba(1,1,0.7,1)
        self.text_color = imgui.get_color_u32_rgba(0,0,0,1)
        
        self.selected = False
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
        
        if self.selected is True:
            self.draw_box(draw_list, color = imgui.get_color_u32_rgba(1,0,0,1), rounding=4, thickness=2)
        draw_list.add_text(self.x_origin+self.layout_padding[0], self.y_origin+self.layout_padding[1], self.text_color,self.name)
            
    def on_mouse_press(self, x, y, button, modifier):
        self.boundary_picked = self.is_boundary_picked(x)
        
    def on_mouse_release(self, x, y, button, modifier):
        if self.is_picked(x,y):
            self.selected = True
        else:
            self.selected = False
            
        if self.boundary_picked is not None:
            self.parent.update_animation_layer(self, self.frame_start, self.frame_end)
            self.boundary_picked = None
            
        if self.translated != 0:
            self.parent.translate_animation_layer(self, self.translated)
            self.translated = 0
            
    def on_mouse_drag(self, x, y, dx, dy):
        if self.selected is True:
            if self.boundary_picked == Boundary.Left:
                self.frame_start += dx
            elif self.boundary_picked == Boundary.Right:
                self.frame_end += dx
            else:
                self.frame_start += dx
                self.frame_end += dx   
                self.translated += dx
            
            
            
