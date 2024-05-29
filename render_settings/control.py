import numpy as np
import math
import pyglet
from pyglet import window, app, shapes
from pyglet.window import mouse,key
from pyglet.math import Mat4, Vec3, Vec4, Quaternion


class Control:
    """
    Control class controls keyboard & mouse inputs.
    """
    def __init__(self, window):
        window.on_key_press = self.on_key_press
        window.on_key_release = self.on_key_release
        window.on_mouse_motion = self.on_mouse_motion
        window.on_mouse_drag = self.on_mouse_drag
        window.on_mouse_press = self.on_mouse_press
        window.on_mouse_release = self.on_mouse_release
        window.on_mouse_scroll = self.on_mouse_scroll
        self.window = window
        self.trackball_size = ((self.window.width ** 2 + self.window.height**2)**0.5) / 2.0
        self.mouse_sensitivity = 0.005
        self.setup()

    def setup(self):
        pass

    def update(self, vector):
        pass

    def on_key_press(self, symbol, modifier):
        pass
    
    def on_key_release(self, symbol, modifier):
        key_interact = {
            pyglet.window.key.ESCAPE: self.window.quit,
            pyglet.window.key.SPACE: lambda: setattr(self.window, 'animate', not self.window.animate),
            pyglet.window.key.R: self.window.reset,
            pyglet.window.key.A: lambda: self.window.GUI.on_key_release(pyglet.window.key.A, modifier),
            pyglet.window.key.D: lambda: self.window.GUI.on_key_release(pyglet.window.key.D, modifier),
            pyglet.window.key.F: lambda: self.window.GUI.on_key_release(pyglet.window.key.F, modifier),
            pyglet.window.key.W: lambda: self.window.GUI.on_key_release(symbol, modifier),
            pyglet.window.key.S: lambda: self.window.GUI.on_key_release(symbol, modifier),
        }
        if symbol in key_interact:
            key_interact[symbol]()

    def on_mouse_motion(self, x, y, dx, dy):
        # TODO:
        pass

    def on_mouse_press(self, x, y, button, modifier):
        if button == 1:  # rotation
            self.window.GUI.on_mouse_down(x, y, button, modifier)
            return

    def on_mouse_release(self, x, y, button, modifier):
        if button == 1:  # rotation
            if self.window.is_ui_active() is True:
                self.window.GUI.on_mouse_release(x, y, button, modifier)
                return

    def on_mouse_drag(self, x, y, dx, dy, button, modifier):
        if button == 1:  # rotation
            if self.window.is_ui_active() is True:
                self.window.GUI.on_mouse_drag(x, y, dx, dy, button, modifier)
                return

            w = self.window.width
            h = self.window.height

            self.window.camera.rotate(w, h, self.trackball_size, x, y, dx, dy)

        elif button == 2:  # translation
            if self.window.is_ui_active() is True:
                return
            
            self.window.camera.translate(dx, dy)


    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        # fov = self.window.get_fov
        # self.window.set_fov = fov - scroll_y

        self.window.camera.zoom(scroll_y)
        