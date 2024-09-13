import pyglet

import imgui
import imgui.core
from imgui.integrations.pyglet import create_renderer


from pyglet_render.keyframe import KeyFrame
from keyframe_viewer import KeyframeViewer
from box_item import BoxItem

from ops import AutoArrangement

from interface import UI
from scene import SCENE
from enum_list import *
class DancerFormation(BoxItem):
    def __init__(self,x_pos, y_pos, x_size, y_size):
        super().__init__()
        self.last_clicked_item = []
        
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.x_size = x_size
        self.y_size = y_size
        self.keyframe_viewer = KeyframeViewer(self)
        self.mode = FormationMode.NORMAL
        
        # Formation drawing
        self.is_drawing = False
        self.boundary_points = []
        self.formation_markers = []
        self.marker_indices = [-1 for _ in range(UI.get_num_dancers())]
        self.marker_label = UI.fonts["dancer_label"]["font"]
        self.marker_radius = 20
                    
    def render(self, x, y):
        x_scale, y_scale = imgui.get_io().display_size 
        x_pos = self.x_pos * x_scale
        y_pos = self.y_pos * y_scale
        x_size = self.x_size * x_scale
        y_size = self.y_size * y_scale
        imgui.set_next_window_position(x_pos,y_pos, imgui.ALWAYS)
        imgui.set_next_window_size(x_size, y_size, imgui.ALWAYS)
        if imgui.begin("Formation Interface", True, flags=imgui.WINDOW_NO_MOVE):
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
            frame = UI.get_frame()
            bound_x, bound_z = SCENE.get_scene_bound()
            scroll_scale = UI.get_cam_eye()[2] / 400
            for dancer in UI.get_dancers():
                dancer.position_scale = [self.xsize_box / (scroll_scale * bound_x + 1e-6), self.ysize_box / (scroll_scale * bound_z + 1e-6)]
                dancer.radius = 30 / (scroll_scale + 1e-6)
                dancer.update_circle_pos()
                dancer.render(draw_list, self.x_origin + self.xsize_box/2, self.y_origin + self.ysize_box/2, frame)
        
            if self.mode == FormationMode.DRAW:
                self.draw_box_filled(draw_list, color=imgui.get_color_u32_rgba(0,0,0,0.8), rounding=5)
                
                text = "Draw Formation" if len(self.formation_markers)==0 or self.is_drawing else "Assign dancer"
                text_size = imgui.calc_text_size(text)
                draw_list.add_text( self.x_origin + self.xsize_box/2-text_size.x/2, self.y_origin + self.ysize_box/5-text_size.y/2, imgui.get_color_u32_rgba(1,1,1,1), text)
                
                if len(self.boundary_points)>1:
                    flag = imgui.DRAW_NONE if self.is_drawing else imgui.DRAW_CLOSED
                    draw_list.add_polyline(points = self.boundary_points, col=imgui.get_color_u32_rgba(1, 0, 0, 1), flags=flag, thickness=2)
                if len(self.formation_markers)>0:
                    color = imgui.get_color_u32_rgba(1, 1, 1, 1)
                    dancers = UI.get_dancers()
                    for idx, point in enumerate(self.formation_markers):
                        draw_list.add_circle_filled(point[0], point[1], radius=self.marker_radius, col=color)
                        if self.marker_indices[idx] != -1:
                            with imgui.font(self.marker_label):
                                name = dancers[self.marker_indices[idx]].name
                                text_size = imgui.calc_text_size(name)
                                draw_list.add_text(point[0]-text_size.x/2, point[1]+self.marker_radius+text_size.y/2, col = color, text = name)
                                        
                        imgui.set_cursor_pos((point[0] - canvas_pos.x - self.marker_radius, point[1] - canvas_pos.y - 20))
                        imgui.invisible_button('marker'+str(idx), 40, 40)
                        with imgui.begin_drag_drop_target() as drag_drop_dst:
                            if drag_drop_dst.hovered:
                                payload = imgui.accept_drag_drop_payload('Dancer index')
                                if payload is not None:
                                    dancer_index = int.from_bytes(payload, 'big')
                                    self.marker_indices[idx] = dancer_index
                                    
            imgui.end()
                    
        return
    
    def reset_markers(self):
        self.marker_indices = [-1 for _ in range(UI.get_num_dancers())]
        
    def get_marker_indices(self):
        return self.marker_indices
    
    def get_frame(self):
        return UI.get_frame()
    
    def set_mode(self, mode):
        self.mode = mode
        self.marker_indices = [-1 for _ in range(UI.get_num_dancers())]
    
    def select(self, selected, modifier = None):
        dancers = UI.get_dancers()
        if modifier is pyglet.window.key.MOD_CTRL: # Multi-select
            if hasattr(selected, 'set_is_clicked'):
                selected.set_is_clicked = True

        else: # Single select
            for dancer in dancers:
                dancer.set_is_clicked = False
            if hasattr(selected, 'set_is_clicked'):
                selected.set_is_clicked = True
                
    def on_key_release(self, symbol, modifiers, frame) -> None:
        dancers = UI.get_dancers()
        if self.mode == FormationMode.NORMAL:
            if symbol==pyglet.window.key.A and modifiers==pyglet.window.key.MOD_CTRL:
                for dancer in dancers:
                    self.select(dancer, modifiers)
        # dx = 5 if symbol==pyglet.window.key.D else -5 if symbol==pyglet.window.key.A else 0
        # dy = 5 if symbol==pyglet.window.key.S else -5 if symbol==pyglet.window.key.W else 0
        # for dancer in dancers:
        #     if dancer.is_selected():
        #         dancer.translate(dx, dy)

    def on_mouse_release(self, x, y, button, modifier) -> None:
        selected = False
        if self.is_picked(x, y):
            if self.mode == FormationMode.NORMAL:
                dancers = UI.get_dancers()
                for dancer in dancers:
                    stage_x = x - (self.x_origin + self.xsize_box/2)
                    stage_y = y - (self.y_origin + self.ysize_box/2)
                    if dancer.is_picked(stage_x, stage_y) and dancer.is_selected() is False:
                        self.select(dancer, modifier)
                        selected = True
                        break
                    
                if not selected:
                    for dancer in dancers:
                        dancer.set_is_clicked = False
                        
            elif self.mode == FormationMode.DRAW:
                if self.is_drawing and len(self.boundary_points) > 2 and UI.get_num_dancers() > 0:
                    self.is_drawing = False
                    autoarr = AutoArrangement(self.boundary_points)            
                    voronoi_points = autoarr.get_arranged_positions(UI.get_num_dancers(), sampling_option="grid_sampling")
                    self.formation_markers = voronoi_points
                    self.marker_indices = [-1 for _ in range(len(voronoi_points))]
            
    def on_mouse_drag(self,x, y, dx, dy):
        if self.is_picked(x, y):
            if self.mode == FormationMode.NORMAL:
                new_picked = None
                prev_picked = []
                dancers  =UI.get_dancers()
                stage_x = x - (self.x_origin + self.xsize_box/2)
                stage_y = y - (self.y_origin + self.ysize_box/2)
                for dancer in dancers:
                    if dancer.is_selected():
                        prev_picked.append(dancer)
                    if dancer.is_picked(stage_x, stage_y):
                        new_picked = dancer
                        
                # If new object is clicked and dragged.
                # if new_picked is not None and new_picked not in prev_picked:
                #     self.select(new_picked)
                # If already selected object is clicked and dragged.
                # else: 
                [dancer.translate(dx, -dy) for dancer in prev_picked]
                
            elif self.mode == FormationMode.DRAW:
                if self.is_drawing:
                    self.boundary_points.append((x, y))
                                
    def on_mouse_press(self, x, y, button, modifier) -> None:
        if self.is_picked(x, y):
            if self.mode == FormationMode.DRAW and button == pyglet.window.mouse.LEFT:
                self.is_drawing = True
                self.boundary_points = [(x, y)]
                    
    def update_ui(self, is_animate, frame) -> None:
        if is_animate:
            dancers = UI.get_dancers()
            for dancer in dancers:
                dancer.animate(frame)
    
    def is_ui_active(self):
        return imgui.is_any_item_active()