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

    def set_parent(self, parent):
        self.parent = parent
        parent.add_child(self)
        self.update_world_transform()
        return

    def add_child(self, child):
        self.children.append(child)
        return
    
    def set_color(self, color):
        self.mesh.colors = color * self.mesh.num_vertices

    def set_transform(self, tf) -> None:
        self.transform = tf

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

    def update_world_transform(self):
        self.transform_gbl = self.transform @ self.parent.transform_gbl if self.parent is not None else self.transform
        for child in self.children:
            child.update_world_transform()

class Character(Object):
    def __init__(self, name, meshes = None, joints = None, scale_link = 1.0):
        super().__init__(mesh_type=MeshType.Sphere,mesh_info={"stack":30, "slice":30, "scale":0.1})
        self.name = name
        self.joints = joints
        self.scale = np.array([1.0,1.0,1.0])
        self.meshes = []

        self.root= None
        
        if meshes is not None:
            self.meshes = meshes
            for m in meshes:
                m.set_parent(self)

        if joints is not None:
            for j in joints:   
                if j.is_root is True:         
                    self.root = j
                    self.root.set_parent(self)
                    break
            self.links = self.create_link(scale_link)

        self.update_world_transform()

    def set_position(self, pos):
        self.transform[3,0:3] = pos
        return
    
    def get_position(self):
        return self.transform_gbl[3,0:3]

    def set_rotation(self, rot):
        pass

    def set_joint_color(self, color):
        for j in self.joints:
            j.set_color(color)

    def set_link_color(self, color):
        for l in self.links:
            l.set_color(color)

    def animate(self, frame):
        
        if self.root is not None:
            if frame < 0 or len(self.root.rotations) <= frame:
                return
            for j in self.joints:
                j.animate(frame)
            self.root.set_scale(self.scale)

    def set_scale(self, scale = [1.0,1.0,1.0]):
        self.scale *= scale
        
        if self.root is not None:
            self.root.set_scale(scale)

    def create_link(self, scale):
        links = []
        for idx, joint in enumerate(self.joints):
            if joint.is_root is True:
                continue
            link = Link(joint.parent, joint, scale)
            links.append(link)
            
        return links

class Joint(Object):
    def __init__(self, name,scale_joint):
        super().__init__(MeshType.Sphere, {"stack":30, "slice":30, "scale":scale_joint})
        self.name = name
        # Ordered list of channels: each
        # list entry is one of [XYZ]position, [XYZ]rotation
        self.channels = []
        self.frames = []
        self.rotations = []
        self.positions = []
        self.offset = np.array([0.,0.,0.]) # static translation vector

        self.order = None
        self.is_root = False
    
    def set_root(self, is_root):
        self.is_root = is_root

    def animate(self, frame):        
        m = np.eye(4, dtype=np.float32)
        m[0:3, 0:3] = Quaternions(self.rotations[frame]).transforms()[0]
        if self.is_root is True:
            m[3, 0:3] = self.positions[frame]
        else:
            m[3, 0:3] = self.transform[3, 0:3]

        self.set_transform(m)

class Link(Object):
    def __init__(self, parent, child, scale):
        super().__init__(MeshType.Cylinder, {"diameter": 1.0, "height": 1.0, "num_segments":16})  
        self.set_parent(parent)
        self.init_transform(parent, child, scale)      

    def init_transform(self, parent, child ,scale):
        p = parent
        c = child

        xp = p.transform_gbl[3,0:3]
        xc = c.transform_gbl[3,0:3]

        offset = xc - xp

        y = mathutil.normalize(offset)

        if np.allclose(y, [0, 0, 1]):
            z_init = np.array([1,0,0])
        else:
            z_init = np.array([0,0,1])

        z = mathutil.normalize(z_init - np.dot(z_init,y))
        x = np.cross(y,z)
        x = mathutil.normalize(x)

        m_s = np.eye(4, dtype = np.float32)
        m_r = np.eye(4, dtype = np.float32)
        m_t = np.eye(4, dtype = np.float32)
        
        m_s[1,1] = np.linalg.norm(offset)
        m_s[0,0] = scale
        m_s[2,2] = scale

        m_r[0,:3] = x
        m_r[1,:3] = y
        m_r[2,:3] = z

        m_t[3,0:3] = c.transform[3, :3] * 0.5
        
        self.transform = np.matmul(np.matmul(m_s, m_r),m_t)