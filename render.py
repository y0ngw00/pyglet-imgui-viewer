import numpy as np
import pyglet
from pyglet import window, app, shapes
from pyglet.window import mouse,key

from pyglet.graphics.shader import Shader, ShaderProgram
from pyglet.gl import GL_TRIANGLES
from pyglet.math import *
from pyglet.gl import *

from primitives import CustomGroup
from scene import Scene
from control import Control
from interface import UI
import shader



class RenderWindow(pyglet.window.Window):
    '''
    inherits pyglet.window.Window which is the default render window of Pyglet
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # glClearColor(219.0/255.0,236.0/255.0,244.0/255.0,1.0)
        glClearColor(0.7,0.7,0.7,1.0)

        self.batch = pyglet.graphics.Batch()
        '''
        View (camera) parameters
        '''
        self.__cam_eye = Vec3(0,150,200)
        self.__cam_target = Vec3(0,40,1.0)
        self.__cam_vup = Vec3(0,1,0)
        self.__view_mat = None
        '''
        Projection parameters
        '''
        self.z_near = 0.1
        self.z_far = 10000
        self.__fov = 60
        self.proj_mat = None
        self.shapes=[]

        # Set up the fog parameters
        self.fog_start = 200.0
        self.fog_end = 500.0
        self.fog_color = (0.7, 0.7, 0.7, 1.0)

        # Light parameters
        self.light_pos = Vec3(0,10000,10000)
        self.light_target = Vec3(0.0, 0, 0)
        self.light_up = Vec3(0.0, 1.0, 0.0)
        light_projection = Mat4.orthogonal_projection(-100, 100, -100, 100,1.0, 100.0)
        light_view = Mat4.look_at(self.light_pos, self.light_target, self.light_up)
        self.light_space_matrix = light_projection @ light_view


        self.setup()
        # Keyboard/Mouse control. Not implemented yet.
        self.controller = Control(self)

        # Scene environment
        self.scene = Scene(self)

        # User interface
        self.GUI = UI(self)

        self.frame = 0
        self.max_frame = 300
        self.animate = False

    def reset(self) -> None:
        self.frame = 0
        self.animate = False
        
    def setup(self) -> None:
        self.set_minimum_size(width = 400, height = 300)
        self.set_mouse_visible(True)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        
    def on_draw(self) -> None:
        self.clear()
        self.batch.draw()
        self.GUI.render()

    def update(self,dt) -> None:
        # 1. Create a view matrix
        self.__view_mat = Mat4.look_at(
            self.__cam_eye, target=self.__cam_target, up=self.__cam_vup)
        
        # 2. Create a projection matrix 
        self.proj_mat = Mat4.perspective_projection(
            aspect = self.width/self.height, 
            z_near=self.z_near, 
            z_far=self.z_far, 
            fov = self.__fov)

        view_proj = self.proj_mat @ self.__view_mat

        if self.animate is True:
            self.frame += 1
        self.scene.animate(self.frame)
        self.scene.update()

        if self.animate:
            self.update_shape()
        for i, shape in enumerate(self.shapes):
            '''
            Update position/orientation in the scene. In the current setting, 
            shapes created later rotate faster while positions are not changed.
            '''                

            # # Example) You can control the vertices of shape.
            # shape.indexed_vertices_list.vertices[0] += 0.5 * dt
            shape.shader_program['view_proj'] = view_proj
            shape.shader_program["lightPos"] = self.light_pos
            # shape.shader_program["viewPos"] = self.get_cam_eye
            # shape.shader_program["lightSpaceMatrix"] = self.light_space_matrix
            shape.shader_program["fogStart"] = self.fog_start
            shape.shader_program["fogEnd"] = self.fog_end
            shape.shader_program["fogColor"] = self.fog_color
            
        self.GUI.update_ui(self.animate)

    def add_shape(self, obj) -> None:
        shape = CustomGroup(obj, len(self.shapes))
        primitive_type = GL_TRIANGLES if obj.mesh.stride==3 else GL_QUADS

        if len(obj.mesh.indices) ==0:
            shape.shader_program.vertex_list(len(obj.mesh.vertices)//3,GL_TRIANGLES,
                        batch = self.batch,
                        group = shape,
                        vertices = ('f', obj.mesh.vertices),
                        colors = ('Bn', obj.mesh.colors),
                        normals = ('f', obj.mesh.normals),
                        uvs = ('f', obj.mesh.uvs),
                        ) 
        else:
            shape.indexed_vertices_list = shape.shader_program.vertex_list_indexed(len(obj.mesh.vertices)//3, GL_TRIANGLES,
                            batch = self.batch,
                            group = shape,
                            indices = obj.mesh.indices,
                            vertices = ('f', obj.mesh.vertices),
                            colors = ('Bn', obj.mesh.colors),
                            normals = ('f', obj.mesh.normals),
                            uvs = ('f', obj.mesh.uvs),
                            )
        self.shapes.append(shape)
        
            
    def update_shape(self):
        for shape in self.shapes:
            shape.indexed_vertices_list.vertices = shape.object.mesh.vertices

    def on_resize(self, width, height):
        glViewport(0, 0, *self.get_framebuffer_size())
        self.proj_mat = Mat4.perspective_projection(
            aspect = width/height, z_near=self.z_near, z_far=self.z_far, fov = self.__fov)
        return pyglet.event.EVENT_HANDLED
         
    def run(self):
        pyglet.clock.schedule_interval(self.update, 1/60)
        pyglet.app.run()

    def quit(self):
        pyglet.app.exit()

    def is_ui_active(self):
        return self.GUI.is_ui_active()


    @property
    def get_fov(self):
        return self.__fov
    
    @get_fov.setter
    def set_fov(self, fov):
        self.__fov = fov
    
    @property
    def get_cam_target(self):
        return self.__cam_target
    
    @get_cam_target.setter
    def set_cam_target(self, v):
        self.__cam_target = v
        
    @property
    def get_cam_eye(self):
        return self.__cam_eye
    
    @get_cam_eye.setter
    def set_cam_eye(self, v):
        self.__cam_eye = v

    @property
    def get_cam_vup(self):
        return self.__cam_vup
    
    @get_cam_vup.setter
    def set_cam_vup(self, v):
        self.__cam_vup = v

    def get_camera_coordinate(self):
        n = (self.__cam_target - self.__cam_eye).normalize()
        u = (self.__cam_vup.cross(n)).normalize()
        v = (n.cross(u)).normalize()

        m = np.vstack((u,v,n)).transpose()
        return m
    
    @property
    def get_view_mat(self):
        return self.__view_mat
    
    @property
    def get_frame(self):
        return self.frame
    
    @get_frame.setter
    def set_frame(self, f):
        self.frame = f
        
    
    def draw_trajectory(self, pos_traj):
        self.scene.draw_trajectory(pos_traj)
        return