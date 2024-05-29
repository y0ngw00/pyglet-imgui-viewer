import numpy as np
import pyglet
from pyglet.math import Mat4, Vec3
from renderables.object import Object,MeshType

from imgui.integrations.pyglet import PygletRenderer
import imgui

import render_settings.shader as shader
import renderables.interface as interface

class Scene:
    def __init__(self, window):
        self.objects=[]
        self.characters = []
        self.window=window

        self.draw_default_scene()
        
    def draw_default_scene(self):
        mat4_identity =  np.eye(4, dtype = np.float32)
        plane = Object(MeshType.GridPlane, {"grid_x":100, "grid_z":40, "scale":5.0})
        plane.set_transform(mat4_identity)
        self.add_object(plane)

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