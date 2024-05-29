import numpy as np
from pyglet.math import Mat4, Vec3, Vec4
import pyglet
from renderables.primitives import CustomMesh,Cube,Sphere, GridPlane, Cylinder

from utils import Quaternions
import legacy.mathutil as mathutil
from enum import Enum
class MeshType(Enum):
    Custom = 0
    Sphere = 1
    Cube = 2
    GridPlane = 3
    Cylinder = 4
    

class Object:
    def __init__(self,mesh_type:MeshType, mesh_info):
        self.children = []
        self.parent = None

        self.transform = np.eye(4, dtype = float)
        self.transform_gbl = np.eye(4, dtype = float)

        mesh_creator = {
            MeshType.Custom: CustomMesh,
            MeshType.Sphere: Sphere,
            MeshType.Cube: Cube,
            MeshType.GridPlane: GridPlane,
            MeshType.Cylinder: Cylinder
        }
        self.mesh = mesh_creator[mesh_type](mesh_info)
        self.texture_id = None
        self.texture = None

    # def set_parent(self, parent):
    #     self.parent = parent
    #     parent.add_child(self)
    #     self.update_world_transform()
    #     return

    # def add_child(self, child):
    #     self.children.append(child)
    #     return
    
    def set_color(self, color):
        self.mesh.colors = color * self.mesh.num_vertices

    def set_transform(self, tf, is_global=True) -> None:
        self.transform = tf
        if is_global:
            self.transform_gbl = self.transform

    def set_position(self, pos) -> None:
        # self.transform = Mat4.from_translation(vector = pos)
        self.transform[3, 0:3] = pos

    def set_scale(self, scale = [1.0,1.0,1.0]):
        s = np.eye(4,dtype=np.float32)
        s[0,0] *= scale[0]
        s[1,1] *= scale[1]
        s[2,2] *= scale[2]
        self.transform = self.transform@s

    def set_texture(self,texture_path):
        img = pyglet.image.load(texture_path)
        self.texture = img.get_texture()

    def animate(self, frame):
        if frame < 0 or hasattr(self.mesh, 'animate') is not True:
            return
        self.mesh.animate(frame)

    # def update_world_transform(self):
    #     self.transform_gbl = self.transform @ self.parent.transform_gbl if self.parent is not None else self.transform
    #     for child in self.children:
    #         child.update_world_transform()

