import numpy as np
import math
import pyglet
from pyglet import window, app, shapes
from pyglet.window import mouse,key
from pyglet.math import Mat4, Vec3, Vec4, Quaternion

import mathutil

    
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
            curr = mathutil.get_trackball_point(self.trackball_size, float(x + dx - w / 2.0), float(y - dy - h / 2.0))
            last = mathutil.get_trackball_point(self.trackball_size, float(x - w / 2.0), float(y - h / 2.0))

            axis = np.cross(curr, last)
            axis = axis / (np.linalg.norm(axis) + 1e-6)
            axis = self.window.get_camera_coordinate().dot(axis)

            last = last / (np.linalg.norm(last) + 1e-6)
            curr = curr / (np.linalg.norm(curr) + 1e-6)

            # sinT = np.linalg.norm(np.cross(curr, last)) / (np.linalg.norm(curr) * np.linalg.norm(last))
            cos_theta = curr.dot(last)
            sin_theta = np.linalg.norm(np.cross(curr, last))
            theta = math.atan2(sin_theta, cos_theta)

            quat = mathutil.angleaxis_to_quat(theta, axis)
            m = Mat4(mathutil.quat_to_mat(quat))

            n = self.window.get_cam_target - self.window.get_cam_eye
            n = mathutil.glet_multiply(m, n)
            self.window.set_cam_vup = mathutil.glet_multiply(m, self.window.get_cam_vup)
            self.window.set_cam_eye = self.window.get_cam_target - n

        elif button == 2:  # translation
            if self.window.is_ui_active() is True:
                return

            v = np.array([0.0, 0.0, 0.0])
            v[0] += dx * 0.1
            v[1] -= dy * 0.1
            v = self.window.get_camera_coordinate().dot(v)

            dt = Vec3(v[0], v[1], v[2])
            self.window.set_cam_target += dt
            self.window.set_cam_eye += dt

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        # fov = self.window.get_fov
        # self.window.set_fov = fov - scroll_y
        dt = (self.window.get_cam_target - self.window.get_cam_eye)* (1-scroll_y * 0.1)
        self.window.set_cam_eye = self.window.get_cam_target - dt
        
