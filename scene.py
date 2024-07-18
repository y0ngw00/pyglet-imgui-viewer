import numpy as np
import pyglet
from pyglet.math import Mat4, Vec3
from object import Object,MeshType

import shader
import ui

class Scene:
    def __init__(self, window):
        self.objects=[]
        self.characters = []
        self.window=window

        self.draw_default_scene()
        # self.draw_root_trajectory()
        
    def draw_default_scene(self):
        mat4_identity =  np.eye(4, dtype = np.float32)
        plane = Object(MeshType.GridPlane, {"grid_x":100, "grid_z":40, "scale":50.0})
        plane.set_transform(mat4_identity)
        self.add_object(plane)
        
      
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
        
    def add_character(self, character):
        
        if character.joints is not None:
            character.set_joint_color((94,161,82,255))
            character.set_link_color((150,75,0,255))
            for j in character.joints:
                self.window.add_shape(j)
            for l in character.links:
                self.window.add_shape(l)
                
        if character.meshes is not None:
            for m in character.meshes:
                self.window.add_shape(m)

        self.characters.append(character)

    def add_object(self, object):
        '''
        Assign a group for each shape
        '''
        self.window.add_shape(object)
        self.objects.append(object)