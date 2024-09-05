import numpy as np
from pyglet.math import Mat4, Vec3, Vec4
import pyglet
from enum import Enum

import copy
import torch

import mathutil
from primitives import CustomMesh,Cube,Sphere, GridPlane, Cylinder

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from motionutils.Quaternions import Quaternions

from enum_list import MeshType
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
        self.texture = None
        self.texture_path = ""
        
        self.selected = False
        
        self.is_show = True

    def show(self, is_show):
        self.is_show = is_show
        
    def set_parent(self, parent):
        self.parent = parent
        parent.add_child(self)
        self.update_world_transform()
        return

    def add_child(self, child):
        self.children.append(child)
        return
    
    def select(self, selected):
        self.selected = selected
        
    def is_selected(self):
        return self.selected
    
    def set_color(self, color):
        self.mesh.colors = color * self.mesh.num_vertices

    def set_transform(self, tf) -> None:
        self.transform = tf

    def set_position(self, pos) -> None:
        self.transform[3, 0:3] = pos

    def set_scale(self, scale = [1.0,1.0,1.0]):
        s = np.eye(4,dtype=np.float32)
        s[0,0] *= scale[0]
        s[1,1] *= scale[1]
        s[2,2] *= scale[2]
        self.transform = self.transform@s

    def set_texture(self,texture_path):
        self.texture_path = texture_path
        img = pyglet.image.load(texture_path)
        self.texture = img.get_texture()

    def animate(self, frame):
        if frame < 0 or hasattr(self.mesh, 'animate') is not True:
            return
        self.mesh.animate(frame)
        
    def get_world_transform(self):
        return self.transform_gbl

    def update_world_transform(self):
        self.transform_gbl = self.transform @ self.parent.transform_gbl if self.parent is not None else self.transform
        for child in self.children:
            child.update_world_transform()

class Character(Object):
    def __init__(self, name, meshes = None, joints = None, scale = [1.0,1.0,1.0], scale_link = 1.0):
        super().__init__(mesh_type=MeshType.Sphere,mesh_info={"stack":30, "slice":30, "scale":0.1})
        self.__name = name
        self.joints = joints
        self.scale = np.array([1.0,1.0,1.0])
        self.meshes = []
        self.is_animate = True

        self.root= None
        self.is_smpl = True
        
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
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
            
        self.set_scale(scale)          
        if self.root is not None:
            self.root.set_scale(scale)

        self.update_world_transform()
        if joints is not None and meshes is not None:
            self.skinning()
            
    def copy(self):
        meshes = []
        joints = []
        for joint in self.joints:
            joints.append(joint.copy())
        [joint.set_parent(joints[joint.parent_index]) for joint in joints if joint.parent_index != -1]
        
        scale = self.scale 
        for mesh_object in self.meshes:
            if mesh_object.texture is not None:
                texture = mesh_object.texture
                texture_path = mesh_object.texture_path
                mesh_object.texture = None
                new_mesh = copy.deepcopy(mesh_object)
                new_mesh.set_texture(texture_path)
                
                mesh_object.texture = texture
                meshes.append(new_mesh)
            else:
                new_mesh = copy.deepcopy(mesh_object)
                meshes.append(new_mesh)
        return Character(self.__name + "_copy", meshes = meshes,joints = joints, scale=scale)
    
    def translate(self, pos):
        # if self.root is not None:
        #     self.root.translate(pos)
        # else:
        self.transform[3,0:3] += pos

        self.update_world_transform()
        if self.joints is not None and self.meshes is not None:
            self.skinning()
        return
        
    def set_position(self, pos):
        # if self.root is not None:
        #     self.root.transform[3,0:3] = pos
        # else:
        if  np.allclose(pos, self.transform[3,0:3], atol=0.001) is not True:
            self.transform[3,0:3] = pos
            self.update_world_transform()
            self.skinning()
        return
    
    @property
    def get_name(self):
        return self.__name
    
    @get_name.setter
    def set_name(self, name):
        self.__name = name
        
    def get_position(self):
        # if self.root is not None:
            # return self.root.transform_gbl[3,0:3]
        # else:
        return self.transform[3,0:3]
    
    def get_root_position(self):
        if self.root is not None:
            return self.root.transform_gbl[3,0:3]
        else:
            return self.transform[3,0:3]

    def set_rotation(self, rot):
        pass
    
    def get_rotation(self, frame):
        return np.concatenate([j.get_rotation(frame) for j in self.joints])
    
    def get_num_joints(self):
        return len(self.joints)

    def set_joint_color(self, color):
        for j in self.joints:
            j.set_color(color)

    def set_link_color(self, color):
        for l in self.links:
            l.set_color(color)
            
    def redefinite_root(self, idx):
        self.root.set_root(False)
        
        self.root = self.joints[idx]
        self.root.set_root(True)
    
    @property    
    def get_is_animate(self):
        return self.is_animate
    
    @get_is_animate.setter
    def set_is_animate(self, is_animate):
        self.is_animate = is_animate

    def set_scale(self, scale = [1.0,1.0,1.0]):
        self.scale *= scale
        super().set_scale(self.scale)
                
        if self.root is not None:
            self.root.set_scale(scale)

    def create_link(self, scale):
        links = []
        for idx, joint in enumerate(self.joints):
            if joint.is_root is True or joint.parent_index == -1:
                continue
            link = Link(joint.parent, joint, scale)
            links.append(link)
            
        return links
    
    def skinning(self):
        if self.is_show is not True:
            return
        
        transform = np.array([j.get_init_transform_inverse() @ j.get_world_transform() for j in self.joints], dtype=np.float32)
        joint_bind_matrices = torch.from_numpy(transform).to(self.device) 
        for m in self.meshes:
            if isinstance(m, Object):
                m.mesh.skin_mesh(joint_bind_matrices)
    
    def animate(self, frame):    
        if self.is_animate is True and self.root is not None:
            if frame < 0 or len(self.root.anim_layers) == 0:
                return
            
            for j_idx, j in enumerate(self.joints):
                j.animate(frame)
            
            self.skinning()
            self.root.set_scale(self.scale)
            
    def add_animation(self, joints, frame, initialize_position = False):
        # if initialize_position is True and len(self.root.positions) >0:
        #     closest_frame = frame
        #     if closest_frame >= len(self.root.positions):
        #         closest_frame = len(self.root.positions) - 1
                
            
        #     root = joints[0]
            
        #     # reflect current xz-plane facing direction to motion data
        #     curr_rot_mat = Quaternions(self.root.rotations[closest_frame]).transforms()[0]
        #     face_dir = curr_rot_mat[:,2] / np.linalg.norm(curr_rot_mat[:,2])
        #     angle = np.arccos(np.dot([0, 0, 1] , face_dir))
        #     if np.cross([0, 0, 1] , face_dir)[1] < 0:
        #         angle = -angle
                
        #     curr_rot = Quaternions.from_angle_axis(angle, np.array([0,1,0]))
        #     curr_rot_mat = curr_rot.transforms()[0]
        #     root.positions = [p @ curr_rot_mat for p in root.positions]
        #     root.rotations = [(curr_rot * Quaternions(q)).qs for q in root.rotations]
            
        #     # position difference update to motion data
        #     curr_pos = self.root.positions[closest_frame]
        #     pos_diff = root.positions[0] - curr_pos
        #     root.positions -= pos_diff
        copied_joints = copy.deepcopy(joints)
        for idx, joint in enumerate(copied_joints):
            if idx > len(self.joints):
                self.joints.append(joint)
                
            else:
                self.joints[idx].add_animation(joint, frame)
                                
    def remove_animation(self, idx):
        for joint in self.joints:
            anim = joint.anim_layers[idx]
            joint.anim_layers.remove(anim)
            
    def clear_all_animation(self):
        for joint in self.joints:
            joint.anim_layers = []
            
    def set_animation_speed(self, idx, speed):
        for joint in self.joints:
            anim = joint.anim_layers[idx]
            anim.set_animation_speed = speed 
            
    def update_animation_layer(self, idx, frame_start, frame_end):
        for joint in self.joints:
            anim = joint.anim_layers[idx].update_play_region(frame_start, frame_end)        

    def translate_animation_layer(self, idx, dx):
        for joint in self.joints:
            anim = joint.anim_layers[idx].translate_region(dx)
            
        
class Joint(Object):
    def __init__(self, name,scale_joint):
        super().__init__(MeshType.Sphere, {"stack":5, "slice":5, "scale":scale_joint})
        self.name = name
        # Ordered list of channels: each
        # list entry is one of [XYZ]position, [XYZ]rotation
        self.channels = []
        self.rotations = []
        self.positions = []
        self.anim_layers = []
        self.offset = np.array([0.,0.,0.]) # static translation vector
        self.init_transform_inv = np.eye(4, dtype = np.float32)

        self.order = None
        self.is_root = False
        self.parent_index = -1
        
    def copy(self):
        name = self.name
        joint = Joint(name,5.0)
        joint.init_transform_inv = self.init_transform_inv
        joint.set_root(self.is_root)
        joint.set_transform(self.transform)
        joint.parent_index = self.parent_index
        return joint
        
    def set_root(self, is_root):
        self.is_root = is_root

    def animate(self, frame):
        for anim_layer in self.anim_layers:
            anim_layer.animate(frame)
        # if frame > len(self.rotations)-1:
        #     return        
        # m = np.eye(4, dtype=np.float32)
        # m[0:3, 0:3] = Quaternions(self.rotations[frame]).transforms()[0]
        # if self.is_root is True:
        #     m[3, 0:3] = self.positions[frame]
        # else:
        #     m[3, 0:3] = self.transform[3, 0:3]

        # self.set_transform(m)
        
    def add_animation(self, joint, frame):
        
        anim_layer = joint.anim_layers
        for anim in anim_layer:
            anim.joint = self
            anim.translate_region(frame)       
            self.anim_layers.append(anim)
        # rest_pos = None
        # rest_rot = None
        # if frame > len(self.rotations):
        #     self.fill_animation(frame)
        # else:
        #     if len(self.rotations) > frame + len(joint.rotations):
        #         if self.is_root is True:
        #             rest_pos = self.positions[frame + len(joint.positions):]
        #         rest_rot = self.rotations[frame + len(joint.rotations):]
 
        #     if self.is_root is True:
        #         self.positions = self.positions[:frame]           
        #     self.rotations = self.rotations[:frame]

                
        # if self.is_root is True:
            # self.positions.extend(joint.positions)
        # self.rotations.extend(joint.rotations)
        
        # if rest_pos is not None:
            # self.positions.extend(rest_pos)
        # if rest_rot is not None:
            # self.rotations.extend(rest_rot)
    
    # def fill_animation(self, frame):
    #     if len(self.rotations) == 0:
    #         self.rotations.append(np.array([1,0,0,0]))
    #         self.positions.append(np.array([0,0,0]))
    #     else:
    #         for i in range(frame - len(self.rotations)):
    #             if self.is_root is True:
    #                 self.positions.append(self.positions[-1])
    #             self.rotations.append(self.rotations[-1])
    #     return
    
    def get_rotation(self, frame):
        for anim_layer in self.anim_layers:
            rot_quat = anim_layer.get_rotation_quaternion(frame)
            if rot_quat is not None:
                return rot_quat
            
        return Quaternions(np.array([1,0,0,0]))
    
    def translate(self, pos):
        self.transform[3,0:3] += pos
        for anim in self.anim_layers:
            anim.translate_position(pos)
        
        return
        
    def get_init_transform_inverse(self):
        return self.init_transform_inv
class Link(Object):
    def __init__(self, parent, child, scale):
        super().__init__(MeshType.Cylinder, {"diameter": 1.0, "height": 1.0, "num_segments":16})  
        self.set_parent(parent)
        self.init_transform(parent, child, scale)      

    def init_transform(self, parent, child, scale):
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