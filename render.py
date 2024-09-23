import os
import numpy as np
import pyglet
from pyglet import window, app, shapes
from pyglet.window import mouse,key

from pyglet.graphics.shader import Shader, ShaderProgram
from pyglet.gl import GL_TRIANGLES
from pyglet.math import *
from pyglet.gl import *
import imageio # For video recording

from enum_list import LayoutMode
from primitives import CustomGroup, CustomMesh
from scene import SCENE
from control import CONTROLLER
from interface import UI
import shader

from audio_manager import AudioManager

class RenderWindow(pyglet.window.Window):
    '''
    inherits pyglet.window.Window which is the default render window of Pyglet
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # glClearColor(219.0/255.0,236.0/255.0,244.0/255.0,1.0)
        # glClearColor(0.9,0.9,0.9,1.0)

        self.batch = pyglet.graphics.Batch()
        '''
        View (camera) parameters
        '''
        self.__cam_eye = Vec3(0,200,700)
        self.__cam_target = Vec3(0,40,1.0)
        self.__cam_vup = Vec3(0,1,0)
        self.__view_mat = None
        '''
        Projection parameters
        '''
        self.z_near = 0.1
        self.z_far = 10000
        self.__fov = 60
        # 2. Create a projection matrix 
        self.proj_mat = Mat4.perspective_projection(
            aspect = self.width/self.height, 
            z_near=self.z_near, 
            z_far=self.z_far, 
            fov = self.__fov)
        self.layout_mode = LayoutMode.FULL
        
        self.shapes=[]

        # Set up the fog parameters
        self.fog_start = 800.0
        self.fog_end = 3000.0
        self.fog_color = (0.7, 0.7, 0.7, 1.0)
        
        self.__use_shadow = False

        # Light parameters
        self.light_pos = Vec3(0,10000,10000)
        self.light_target = Vec3(0.0, 0, 0)
        self.light_up = Vec3(0.0, 1.0, 0.0)
        light_projection = Mat4.orthogonal_projection(-100, 100, -100, 100,1.0, 100.0)
        light_view = Mat4.look_at(self.light_pos, self.light_target, self.light_up)
        self.light_space_matrix = light_projection @ light_view

        self.frame = 0
        self.max_frame = 300
        self.framerate = 30.0
        self.fps = 1.0/self.framerate
        self.animate = False
        self.show_scene = True
        self.show_ui = True
        
        # Video recording
        self.is_record = False

        self.setup()
        
        # User interface
        self.audio_manager = AudioManager(self, framerate = self.framerate)
        self.update_audio = False

    def reset(self) -> None:
        self.frame = 0
        self.animate = False
        self.audio_manager.reset()
        
    def play(self) -> None:
        self.animate = not self.animate
        if self.animate:
            self.audio_manager.play()
        else:
            self.audio_manager.pause()
            
    def show(self) -> None:
        self.show_scene = not self.show_scene
        SCENE.show(self.show_scene)
         
    def setup(self) -> None:
        self.set_minimum_size(width = 400, height = 300)
        self.set_mouse_visible(True)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        
    def on_draw(self) -> None:
        self.clear()
        if self.show_scene is True:
            self.batch.draw()
        if self.show_ui is True:
            UI.render()
            
        if self.is_record is True:
            self.record()

    def update(self,dt) -> None:
        self.fps = 1.0/dt
        # 1. Create a view matrix       
        self.__view_mat = Mat4.look_at(
            self.__cam_eye, target=self.__cam_target, up=self.__cam_vup)
        
        view_proj = self.proj_mat @ self.__view_mat
        
        if self.animate is True:
            SCENE.animate(self.frame)
            SCENE.update()
        if self.show_scene is True:
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
        
        if self.show_ui is True:
            UI.update_ui(self.animate)
            
        if self.update_audio is True:
            self.audio_manager.update(self.frame, self.update_audio)
            self.update_audio = False

        if self.animate is True:
            self.frame += 1     
        
    def set_update_audio_flag(self, flag):
        self.update_audio = flag

    def add_shape(self, obj) -> None:
        shape = CustomGroup(obj, len(self.shapes))

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
        
    def initialize_audio(self, file_path):
        self.audio_manager.open_audio_file(file_path)
        
    def update_shape(self):
        for shape in self.shapes:
            shape.indexed_vertices_list.vertices = shape.object.mesh.vertices
            
    def capture_screen(self, filename = "screenshot.png") -> None:
        """
        Captures the current screen and saves it as a PNG image.

        Returns:
            None
        """
        # glBindFramebuffer(GL_FRAMEBUFFER, 0)
        # glReadBuffer(GL_FRONT)
        data = (GLubyte * (3 * self.width * self.height))()
        glReadPixels(0, 0, self.width, self.height, GL_RGB, GL_UNSIGNED_BYTE, data)

        # Save the texture to an image file

        save_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'save/')
        if os.path.exists(save_dir) is not True:
            os.makedirs(save_dir, exist_ok=True)
        save_path = save_dir + filename
        
        while os.path.exists(save_path):
            save_path = save_path[:-4] + "_.png"
        image = pyglet.image.ImageData(self.width, self.height, 'RGB', data)
        image.save(save_path)

    def record(self):
        """
        Records the current frame and appends it to the video writer.

        This method retrieves the color buffer from the pyglet window, converts it to an image data object,
        and then converts the image data to a numpy array. The array is then flipped vertically to make the
        image correctly oriented. Finally, the frame is appended to the video writer.
        """
        self.capture_screen(str(self.frame) + ".png")
        
        if self.frame >= UI.get_end_frame():
            self.stop_recording()

    def on_resize(self, width, height):
        width,height = self.get_framebuffer_size()
        
        if self.layout_mode == LayoutMode.FULL:
            x_0, y_0 = int(width *660/2560), int(height * (1 - 960/1440))
            x_1, y_1 = int(width *1900/2560), int(height * (1 - 30/1440))
            self.proj_mat = Mat4.perspective_projection(
            aspect = width/height, z_near=self.z_near, z_far=self.z_far, fov = self.__fov)
        elif self.layout_mode == LayoutMode.HALF:
            x_0, y_0 = int(width *1610/2560), int(height * (1 - 960/1440))
            x_1, y_1 = int(width *950/2560), int(height * (1 - 30/1440))
            self.proj_mat = Mat4.perspective_projection(
            aspect = 0.5 * width/height, z_near=self.z_near, z_far=self.z_far, fov = self.__fov)
        glViewport(x_0, y_0, x_1, y_1)
        # glViewport(0, 0, *self.get_framebuffer_size())
        
        return pyglet.event.EVENT_HANDLED
    
    def adjust_scene_layout(self, layout_mode = LayoutMode.FULL):
        if layout_mode == LayoutMode.FULL:
            self.layout_mode = LayoutMode.FULL
        elif layout_mode == LayoutMode.HALF:
            self.layout_mode = LayoutMode.HALF
        self.on_resize(self.width, self.height)
        
    def run(self):                
        pyglet.clock.schedule_interval(self.update, 1/self.framerate)
        pyglet.app.run()

    def quit(self):
        pyglet.app.exit()

    def is_ui_active(self):
        return UI.is_ui_active()
    
    def start_recording(self):        
        self.is_record = True
        self.reset()
        self.play()
        
    def stop_recording(self):
        self.is_record = False
        
        save_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'save/')
        if os.path.exists(save_dir) is not True:
            os.makedirs(save_dir, exist_ok=True)
            
        import time
        current_time = time.strftime("%m%d-%H%M%S")
        save_path = save_dir + str(current_time) + ".mp4"
        
        import cv2
        fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
        video = cv2.VideoWriter(save_path, fourcc, 30, (self.width, self.height))

        for frame in range(UI.get_end_frame()+1):
            image_path = save_dir + str(frame) + ".png"
            image = cv2.imread(image_path)
            video.write(image)
            if os.path.exists(image_path):
                os.remove(image_path)
            
        video.release()
        self.reset()
        self.play()
        
        
    def get_audio_framelength(self):
        return self.audio_manager.duration * self.framerate
        
    @property
    def use_shadow(self):
        return self.__use_shadow
    
    @use_shadow.setter
    def set_shadow(self, flag):
        self.__use_shadow = flag

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
        SCENE.draw_trajectory(pos_traj)
        return