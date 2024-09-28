import os

import numpy as np
import pickle as pkl
import pyglet
from pyglet.math import Mat4, Vec3
from object import Object,MeshType,Character

class Scene:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Scene, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.objects=[]
        self.characters = []
        self.window = None
        
        self.__x_bound = 600
        self.__z_bound = 300
        
    def clear_scene(self):
        self.window.clear_scene() # store temporarily and connect it back after initializing the scene

        temp_window = self.window # store temporarily and connect it back after initializing the scene
        self.__init__()        
        self.connect_renderer(temp_window)
        
    def load_project(self, data):
        self.clear_scene()
        
        self.__dict__.update(data["scene"])
        from interface import UI
        character_data = data["scene"]["characters"]
        self.characters=[]
        for chr_data in character_data:
            if "original_file_path" in chr_data:
                file_path = chr_data["original_file_path"]
                UI.open_file(file_path)
            else:
                character = Character.load(chr_data)
                self.add_character(character)
        
    def save_project(self, data):
        state = self.__dict__.copy()
        
        if 'window' in state:
            del state['window']
        if 'objects' in state:
            del state['objects']
        if 'characters' in state:
            state['characters'] = [character.save() for character in self.characters]
            
        data["scene"] = state 
        
    def connect_renderer(self, window):
        self.window=window
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
        wall.set_position([0,50,-3000])
        wall.update_world_transform()
        
        wall_r = Object(MeshType.Cube, {"scale":[1.0, 6000.0, 6000.0]})
        self.add_object(wall_r)
        wall_r.set_position([3000,50,0])
        wall_r.update_world_transform()
        
        wall_l = Object(MeshType.Cube, {"scale":[1.0, 6000.0, 6000.0]})
        self.add_object(wall_l)
        wall_l.set_position([-3000,50,0])
        wall_l.update_world_transform()
        
      
    def draw_root_trajectory(self):
        '''
        Draw a root trajectory
        '''    
        # sphere = Object(MeshType.Sphere, {"stack":3, "slice":3, "scale":0.1})
        pass
            
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
        
    def get_scene_bound(self):
        return self.x_bound, self.z_bound
   
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
    
    @classmethod
    def get_instance(cls):
        # Initialize the singleton if not already done
        if cls._instance is None:
            cls._instance = Scene()
        return cls._instance
                

SCENE = Scene.get_instance()