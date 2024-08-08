import pyglet

import imgui
import imgui.core
from imgui.integrations.pyglet import create_renderer


from fonts import Fonts
from keyframe import KeyFrame
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
            for dancer in self.parent_window.get_dancers():
                dancer.render(draw_list, self.x_origin + self.xsize_box/2, self.y_origin + self.ysize_box/2, frame)
                
            imgui.end()
            
        # bChanged = self.keyframe_viewer.render()
        # if bChanged:
        #     self.update_ui(self.keyframe_viewer.is_keyframe_animate)
                    
        return
    
    def get_frame(self):
        return self.parent_window.get_frame()
    
    def select(self, selected, modifier = None):
        dancers = self.parent_window.get_dancers()
        if modifier is imgui.KEY_MOD_SHIFT: # Multi-select
            if hasattr(selected, 'set_is_clicked'):
                selected.set_is_clicked = True

        else: # Single select
            for dancer in dancers:
                dancer.set_is_clicked = False
            if hasattr(selected, 'set_is_clicked'):
                selected.set_is_clicked = True

    def on_key_release(self, symbol, modifiers, frame) -> None:
        dancers = self.parent_window.get_dancers()
        
        # dx = 5 if symbol==pyglet.window.key.D else -5 if symbol==pyglet.window.key.A else 0
        # dy = 5 if symbol==pyglet.window.key.S else -5 if symbol==pyglet.window.key.W else 0
        # for dancer in dancers:
        #     if dancer.is_selected():
        #         dancer.translate(dx, dy)

    def on_mouse_release(self, x, y, button, modifier) -> None:
        pass
            
    def on_mouse_drag(self,x, y, dx, dy):
        if self.is_picked(x, y):
            dancers = self.parent_window.get_dancers()
            [dancer.translate(dx, -dy) for dancer in dancers if dancer.is_selected()]
                
    def on_mouse_press(self, x, y, button, modifier) -> None:
        selected = False
        if self.is_picked(x, y):
            dancers = self.parent_window.get_dancers()
            for dancer in dancers:
                stage_x = x - (self.x_origin + self.xsize_box/2)
                stage_y = y - (self.y_origin + self.ysize_box/2),
                if dancer.is_picked(stage_x, stage_y):
                    self.select(dancer, modifier)
                    selected = True
                    break
                
            if not selected:
                for dancer in dancers:
                    dancer.set_is_clicked = False
                    
    def update_ui(self, is_animate, frame) -> None:
        if is_animate:
            dancers = self.parent_window.get_dancers()
            for dancer in dancers:
                dancer.animate(frame)
    
    def is_ui_active(self):
        return imgui.is_any_item_active()