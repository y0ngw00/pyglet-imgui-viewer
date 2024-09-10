import numpy as np
import pyglet
from pyglet.math import Mat4, Vec3
from object import Object,MeshType

import shader
import ui
import os

class Scene:
    def __init__(self, window):
        self.objects=[]
        self.characters = []
        self.window=window
        
        self.__x_bound = 3000
        self.__z_bound = 3000

        self.draw_default_scene()
        # self.draw_root_trajectory()
        
    def draw_default_scene(self):
        mat4_identity =  np.eye(4, dtype = np.float32)
        # plane = Object(MeshType.GridPlane, {"grid_x":6, "grid_z":6, "scale":1000.0, 
        #                                     "black_color":(191, 191,191, 255), "white_color":(191, 191,191, 255)})
        # plane.set_transform(mat4_identity)
        # curr_path = os.path.dirname(os.path.abspath(__file__))
        # plane.set_texture(curr_path+"/textures/floor2.jpg")
        plane = Object(MeshType.GridPlane, {"grid_x":60, "grid_z":60, "scale":100.0})
        plane.set_transform(mat4_identity)
        curr_path = os.path.dirname(os.path.abspath(__file__))
        plane.set_texture(curr_path+"/textures/floor.jpeg")
        self.add_object(plane)
        
        wall = Object(MeshType.Cube, {"scale":[6000.0, 6000.0, 1.0]})
        # wall.set_transform(mat4_identity)
        self.add_object(wall)
        wall.set_position([0,50,-self.z_bound])
        wall.update_world_transform()
        
        wall_r = Object(MeshType.Cube, {"scale":[1.0, 6000.0, 6000.0]})
        self.add_object(wall_r)
        wall_r.set_position([self.x_bound,50,0])
        wall_r.update_world_transform()
        
        wall_l = Object(MeshType.Cube, {"scale":[1.0, 6000.0, 6000.0]})
        self.add_object(wall_l)
        wall_l.set_position([-self.x_bound,50,0])
        wall_l.update_world_transform()
        
      
    def draw_root_trajectory(self):
        '''
        Draw a root trajectory
        '''
        radius = 3.0
        nframe = 150
        fps = 30
        vx = -radius * np.ones(nframe)
        vz = radius * np.ones(nframe)
        half = nframe//2
        vz[half:] *= -1
        
        # radius = 10.0
        # angle = np.linspace(0, 2*np.pi, nframe+1)
        # vx = radius - radius * np.cos(angle)
        # vz = radius * np.sin(angle)
        
        
        traj = np.zeros([nframe,2], dtype = np.float32)
        traj[0,0] = 0
        traj[0,1] = 0
        for n in range(nframe-1):
            traj[n+1,0] = traj[n,0] + vx[n]/fps
            traj[n+1,1] = traj[n,1] + vz[n]/fps
    
        for _traj in traj:
            sphere = Object(MeshType.Sphere, {"stack":3, "slice":3, "scale":0.1})
            sphere.set_color((200,0,0,255))
            sphere.set_position([_traj[0],0.0,_traj[1]])
            self.add_object(sphere)
            
    def draw_trajectory(self, pos_traj):
        '''
        Draw a trajectory
        '''
        
        for _traj in pos_traj:
            sphere = Object(MeshType.Sphere, {"stack":3, "slice":3, "scale":1.0})
            sphere.set_color((200,0,0,255))
            sphere.set_position([_traj[0],0.0,_traj[2]])
            self.add_object(sphere)

            
    def reset(self):
        ## Just for debugging. Character reset.
        # self.characters = []
        return
    
    def show(self, is_show):
        for character in self.characters:
            character.show(is_show)

        for object in self.objects:
            object.show(is_show)

    def animate(self, frame):
        for character in self.characters:
            character.animate(frame)

        for object in self.objects:
            object.animate(frame)
        

    def update(self): 
        for character in self.characters:
            character.update_world_transform()

        # for object in self.objects:
        #     object.update_world_transform()
        
    def get_num_characters(self):
        return len(self.characters)
    
    def get_character(self, idx):
        if idx < len(self.characters):
            return self.characters[idx]
        else:
            return None
        
    def add_character(self, character):
                
        if len(character.meshes) > 0:
            for m in character.meshes:
                self.window.add_shape(m)
        
        else:
            if character.joints is not None:
                character.set_joint_color((94,161,82,255))
                character.set_link_color((150,75,0,255))
            for j in character.joints:
                self.window.add_shape(j)
            for l in character.links:
                self.window.add_shape(l)

        self.characters.append(character)

    def add_object(self, object):
        '''
        Assign a group for each shape
        '''
        self.window.add_shape(object)
        self.objects.append(object)
        
    @property
    def x_bound(self):
        return self.__x_bound
    @x_bound.setter
    def x_bound(self, x_bound):
        self.__x_bound = x_bound
    @property
    def z_bound(self):
        return self.__z_bound
    @z_bound.setter
    def y_bound(self, z_bound):
        self.__z_bound = z_bound
    