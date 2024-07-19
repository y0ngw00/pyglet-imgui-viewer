import pyglet

import imgui
import imgui.core
from imgui.integrations.pyglet import create_renderer

from keyframe import KeyFrame
from dancer_circle import DancerCircle
from keyframe_viewer import KeyframeViewer

class DancerFormation:
    def __init__(self, parent_window):
        self.circles = []   
        self.xsize_box = 500
        self.ysize_box = 500
                
        self.x_box = 0
        self.y_box = 0
                
        self.last_clicked_item = []
        
        self.parent_window = parent_window
        self.keyframe_viewer = KeyframeViewer(self)
                    
    def render(self, x, y):
        if imgui.begin("Drawing Interface", True, flags=imgui.WINDOW_NO_MOVE):
            draw_list = imgui.get_window_draw_list()
            canvas_pos = imgui.get_cursor_screen_pos()  # Get the position of the canvas window

            layout_padding = [10,10]
            x_origin = canvas_pos.x+layout_padding[0]
            y_origin = canvas_pos.y+layout_padding[1]
            
            self.x_box = x_origin
            self.y_box = y_origin
            
            draw_list.add_rect(x_origin, y_origin, x_origin+self.xsize_box, y_origin+self.ysize_box, imgui.get_color_u32_rgba(1,0,0,1), rounding=5, thickness=3)
            
            frame = self.parent_window.get_frame()
            

            # Draw a dot
            for circle in self.circles:
                color =  imgui.get_color_u32_rgba(1,1,1,1)
                
                if len(circle.sync_keyframe.keyframes) > 1:
                    left, right = circle.sync_keyframe.get_nearest_keyframe(frame)
                    if left %2 ==0 and right %2 ==1:
                        color = imgui.get_color_u32_rgba(1,0.7,0,1)
                        
                
                if circle in self.last_clicked_item and self.parent_window.is_playing() is False:
                    color = imgui.get_color_u32_rgba(1,1,0,1)
                    
                draw_list.add_circle_filled(x_origin+circle.x, y_origin+circle.y, circle.radius,color)

            imgui.end()
            
        bChanged = self.keyframe_viewer.render()
        
        if bChanged:
            self.update_ui(self.keyframe_viewer.is_keyframe_animate)

        
        return
    
    def add_dancer(self, character):
        self.circles.append(DancerCircle(character,self.xsize_box, self.ysize_box, 1))
    
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
                    circle.add_keyframe(KeyFrame(frame, (circle.x, circle.y)))
            else:
                if len(self.last_clicked_item) >0:
                    for circle in self.last_clicked_item:
                        circle.add_keyframe(KeyFrame(frame, (circle.x, circle.y)))
                    
        if symbol == pyglet.window.key.G:
            if modifiers == pyglet.window.key.MOD_CTRL:
                for circle in self.circles:
                    circle.add_sync_keyframe(KeyFrame(frame, (circle.x, circle.y)))
            else:
                if len(self.last_clicked_item) >0:
                    for circle in self.last_clicked_item:
                        circle.add_sync_keyframe(KeyFrame(frame, (circle.x, circle.y)))
        
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
        if self.is_in_formation_box(x, y):
            for circle in self.last_clicked_item:
                circle.translate(dx, -dy)
                
    def on_mouse_down(self, x, y, button, modifier) -> None:
        for circle in self.circles:
            if (x-self.x_box-circle.x)**2 + (y - self.y_box-circle.y)**2 < circle.radius**2:
                circle.set_is_clicked = True
            else:
                circle.set_is_clicked = False
                
    def update_ui(self, is_animate, frame) -> None:
        if is_animate:
            for circle in self.circles:
                circle.animate(frame)

    def is_in_formation_box(self, x, y) -> bool:
        if self.x_box<=x<=self.x_box+self.xsize_box and self.y_box<=y<=self.y_box+self.ysize_box:
            return True
        return False
    
    def is_ui_active(self):
        return imgui.is_any_item_active()