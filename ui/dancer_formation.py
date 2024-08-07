import pyglet

import imgui
import imgui.core
from imgui.integrations.pyglet import create_renderer

from keyframe import KeyFrame
from dancer_circle import DancerCircle
from keyframe_viewer import KeyframeViewer
from box_item import BoxItem
class DancerFormation(BoxItem):
    def __init__(self, parent_window,x_pos, y_pos, x_size, y_size):
        super().__init__()
        self.last_clicked_item = []
        
        self.parent_window = parent_window
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.x_size = x_size
        self.y_size = y_size
        self.keyframe_viewer = KeyframeViewer(self)
                    
    def render(self, x, y):
        x_scale, y_scale = imgui.get_io().display_size 
        x_pos = self.x_pos * x_scale
        y_pos = self.y_pos * y_scale
        x_size = self.x_size * x_scale
        y_size = self.y_size * y_scale
        imgui.set_next_window_position(x_pos,y_pos, imgui.ALWAYS)
        imgui.set_next_window_size(x_size, y_size, imgui.ALWAYS)
        if imgui.begin("Drawing Interface", True, flags=imgui.WINDOW_NO_MOVE):
            draw_list = imgui.get_window_draw_list()
            canvas_pos = imgui.get_window_position()  # Get the position of the canvas window
            window_size = imgui.get_window_size()

            layout_padding = [10,30]
            self.update_position(x = canvas_pos.x+layout_padding[0],
                                 y = canvas_pos.y+layout_padding[1],
                                 xsize_box = window_size.x - 2*layout_padding[0],
                                 ysize_box = window_size.y - 2*layout_padding[1])
            self.draw_box(draw_list, color=imgui.get_color_u32_rgba(1,1,1,1), rounding=5, thickness=3)
            
            # Draw a dot
            frame = self.parent_window.get_frame()
            for circle in self.circles:
                circle.render(draw_list, self.x_origin, self.y_origin, frame)
                
            imgui.end()
            
        bChanged = self.keyframe_viewer.render()
        if bChanged:
            self.update_ui(self.keyframe_viewer.is_keyframe_animate)
                    
        return
    
    def add_dancer(self, character):
        self.circles.append(DancerCircle(character,self.xsize_box, self.ysize_box, 0.5))
    
    def get_num_dancers(self):
        return len(self.circles)
    
    def get_circles(self):
        return self.circles
    
    def get_frame(self):
        return self.parent_window.get_frame()
    
    def on_key_release(self, symbol, modifiers, frame) -> None:
        if symbol == pyglet.window.key.F:
            if modifiers == pyglet.window.key.MOD_CTRL:
                for circle in self.circles:
                    circle.add_keyframe(frame)
            else:
                if len(self.last_clicked_item) >0:
                    for circle in self.last_clicked_item:
                        circle.add_keyframe(frame)
                    
        if symbol == pyglet.window.key.G:
            if modifiers == pyglet.window.key.MOD_CTRL:
                for circle in self.circles:
                    circle.add_sync_keyframe(frame)
            else:
                if len(self.last_clicked_item) >0:
                    for circle in self.last_clicked_item:
                        circle.add_sync_keyframe(frame)
        
        dx = 5 if symbol==pyglet.window.key.D else -5 if symbol==pyglet.window.key.A else 0
        dy = 5 if symbol==pyglet.window.key.S else -5 if symbol==pyglet.window.key.W else 0
        if len(self.last_clicked_item) >0:
            for circle in self.last_clicked_item:
                circle.translate(dx, dy)
    
    def on_mouse_release(self, x, y, button, modifier) -> None:
        for circle in self.circles:
            if circle.get_is_clicked:
                if modifier is not pyglet.window.key.MOD_SHIFT and modifier != 17:
                    self.last_clicked_item = []
                self.last_clicked_item.append(circle)
            circle.set_is_clicked = False
            
        if self.is_ui_active() is False:
            self.last_clicked_item = []
            
    def on_mouse_drag(self,x, y, dx, dy):
        if self.is_picked(x, y):
            for circle in self.last_clicked_item:
                circle.translate(dx, -dy)
                
    def on_mouse_press(self, x, y, button, modifier) -> None:
        for circle in self.circles:
            if (x-self.x_origin-circle.x)**2 + (y - self.y_origin-circle.y)**2 < circle.radius**2:
                circle.set_is_clicked = True
            else:
                circle.set_is_clicked = False
                
    def update_ui(self, is_animate, frame) -> None:
        if is_animate:
            for circle in self.circles:
                circle.animate(frame)
    
    def is_ui_active(self):
        return imgui.is_any_item_active()