import base64
import os
import random

import numpy as np

from utils import BVH
from object import Character,Joint,Link,Object,MeshType
import mathutil

def load_bvh(filepath, scale = [1.0,1.0,1.0]):
    if not os.path.exists(filepath):
        return None
    
    ext = filepath.split('.')[-1]
    name = filepath.split('/')[-1]
    if ext == "bvh":
        data = BVH.load(filepath)
        joints = create_joint(data[0], data[1],scale_joint = 5.0)
        character = Character(name, joints = joints,scale=scale, scale_link = 5.0)
        print("BVH load success.")

        data={}

        return character

def create_joint(data,names,scale_joint):
    joints = []
    n_joint = len(names)
    for idx, name in enumerate(names):
        joint = Joint(name,scale_joint)
        if data.parents[idx] == -1:
            joint.set_root(True)
            joint.set_position(data.offsets[idx])
        else:
            joint.set_parent(joints[data.parents[idx]])
            joint.set_position(data.offsets[idx])
        
        joints.append(joint)

    for frame, rot in enumerate(data.rotations):
        for idx, joint in enumerate(joints):
            joint.rotations.append(rot[idx])

            if joint.is_root is True:
                joint.positions.append(data.positions[frame][idx])

    return joints