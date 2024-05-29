import numpy as np
from pyglet.math import Vec3, Mat4, Vec4
import math
from fairmotion.ops import conversions

def get_trackball_point(r, dx, dy):
    dxdx_dydy = dx*dx + dy*dy
    if r*r > dxdx_dydy:
        return np.array([dx/r, dy/r, (r*r - dxdx_dydy)**0.5 / r])
    else:
        return np.array([dx/r, dy/r, 0.0])

def glet_multiply(m,v):
    if len(v) ==4:
        result = Vec4(0)
        for i in range(4):
            result[i] = (m[i*4] * v[0] +
                        m[i*4 + 1] * v[1] +
                        m[i*4 + 2] * v[2] +
                        m[i*4 + 3] * v[3])
    elif len(v)==3:
        stride = 4 if len(m)==16 else 3
        result = Vec3(0)
        for i in range(3):
            result[i] = (m[i*stride] * v[0] +
                        m[i*stride + 1] * v[1] +
                        m[i*stride + 2] * v[2])
    return result

class Camera:
    def __init__(self, eye, target, up=Vec3(0, 1, 0), fov=60):
        self.eye = eye
        self.target = target
        self.up = up
        self.fov = fov
        self.z_near = 0.1
        self.z_far = 10000
        
    def look_at(self):
        return Mat4.look_at(self.eye, self.target, self.up)

    def perspective_projection(self, aspect):
        proj_mat = Mat4.perspective_projection(
        aspect = aspect, 
        z_near=self.z_near, 
        z_far=self.z_far, 
        fov = self.fov)
        return proj_mat

    def get_camera_coordinate(self):
        n = (self.target - self.eye).normalize()
        u = (self.up.cross(n)).normalize()
        v = (n.cross(u)).normalize()

        m = np.vstack((u,v,n)).transpose()
        return m
    
    def translate(self, dx, dy):
        v = np.array([0.0, 0.0, 0.0])
        v[0] += dx * 0.01
        v[1] -= dy * 0.01
        v = self.get_camera_coordinate().dot(v)

        dt = Vec3(v[0], v[1], v[2])
        self.target += dt
        self.eye += dt


    def rotate(self, w, h, trackball_size, x, y, dx, dy):
            curr = get_trackball_point(trackball_size, float(x + dx - w / 2.0), float(y - dy - h / 2.0))
            last = get_trackball_point(trackball_size, float(x - w / 2.0), float(y - h / 2.0))

            axis = np.cross(curr, last)
            axis = axis / (np.linalg.norm(axis) + 1e-6)
            axis = self.get_camera_coordinate().dot(axis)

            last = last / (np.linalg.norm(last) + 1e-6)
            curr = curr / (np.linalg.norm(curr) + 1e-6)

            # sinT = np.linalg.norm(np.cross(curr, last)) / (np.linalg.norm(curr) * np.linalg.norm(last))
            cos_theta = curr.dot(last)
            sin_theta = np.linalg.norm(np.cross(curr, last))
            theta = math.atan2(sin_theta, cos_theta)
            
            m = conversions.A2T(theta * axis)
            m = Mat4(m.flatten())
            # quat = mathutil.angleaxis_to_quat(theta, axis)
            # m = Mat4(mathutil.quat_to_mat(quat))

            n = self.target - self.eye
            n = glet_multiply(m, n)
            self.up = glet_multiply(m, self.up)
            self.eye = self.target - n

    def zoom(self, scroll):
        dt = (self.target - self.window.eye)* (1-scroll * 0.1)
        self.eye = self.target - dt
