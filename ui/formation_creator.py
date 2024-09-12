import pyglet
import imgui
from imgui.integrations.pyglet import create_renderer
from pyglet_render.keyframe import KeyFrame
from box_item import BoxItem

from ops import AutoArrangement

import imgui.core

from interface import UI
class FormationCreator(BoxItem):
    def __init__(self, x_pos, y_pos, x_size, y_size):
        super().__init__()
        self.last_clicked_item = []
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.x_size = x_size
        self.y_size = y_size
        self.__show = False
        self.is_drawing = False
        self.boundary_points = []
        self.dancer_points = []

    def render(self):
        x_scale, y_scale = imgui.get_io().display_size
        x_pos = self.x_pos * x_scale
        y_pos = self.y_pos * y_scale
        x_size = self.x_size * x_scale
        y_size = self.y_size * y_scale
        imgui.set_next_window_position(x_pos, y_pos, imgui.ALWAYS)
        imgui.set_next_window_size(x_size, y_size, imgui.ALWAYS)

        if self.__show is True:
            if imgui.begin("Drawing Interface", True, flags=imgui.WINDOW_NO_MOVE):
                draw_list = imgui.get_window_draw_list()
                canvas_pos = imgui.get_window_position()  # Get the position of the canvas window
                window_size = imgui.get_window_size()

                layout_padding = [10, 30]
                self.update_position(
                    x=canvas_pos.x + layout_padding[0],
                    y=canvas_pos.y + layout_padding[1],
                    xsize_box=window_size.x - 2 * layout_padding[0],
                    ysize_box=window_size.y - 2 * layout_padding[1]
                )
                self.draw_box(draw_list, color=imgui.get_color_u32_rgba(1, 1, 1, 1), rounding=5, thickness=3)

                if len(self.boundary_points)>1:
                    flag = imgui.DRAW_NONE if self.is_drawing else imgui.DRAW_CLOSED
                    draw_list.add_polyline(points = self.boundary_points, col=imgui.get_color_u32_rgba(1, 0, 0, 1), flags=flag, thickness=2)
                if len(self.dancer_points)>0:
                    for point in self.dancer_points:
                        draw_list.add_circle_filled(point[0], point[1], radius=3, col=imgui.get_color_u32_rgba(0, 1, 0, 1))
                imgui.end()

        return

    def get_frame(self):
        return UI.get_frame()

    @property
    def is_show(self):
        return self.__show

    def show(self, is_show):
        self.__show = is_show

    def select(self, selected, modifier=None):
        pass

    def on_key_release(self, symbol, modifiers, frame) -> None:
        pass

    def on_mouse_release(self, x, y, button, modifier) -> None:
        if button == pyglet.window.mouse.LEFT:
            self.is_drawing = False
            import numpy as np
            autoarr = AutoArrangement(np.array(self.boundary_points))
            points = autoarr.generate_random_points(5)
            voronoi_points = autoarr.lloyd_relaxation(points)
            self.dancer_points = voronoi_points

    def on_mouse_drag(self, x, y, dx, dy):
        if self.is_drawing:
            self.boundary_points.append((x, y))

    def on_mouse_press(self, x, y, button, modifier) -> None:
        if button == pyglet.window.mouse.LEFT:
            self.is_drawing = True
            self.boundary_points = [(x, y)]

    def update_ui(self, is_animate, frame) -> None:
        pass

    def is_ui_active(self):
        return imgui.is_any_item_active()