import base64
import os
import random

import numpy as np
from pygltflib import GLTF2, Node, Skin, Accessor, BufferView, BufferFormat

from utils import BVH
from object import Character,Joint,Link,Object,MeshType
import legacy.mathutil as mathutil

def load_gltf(filename):
    gltf = GLTF2().load(filename)
    name = filename.split('/')[-1]
    meshes = load_gltf_mesh(filename, gltf)

    joints = load_gltf_joint(filename, gltf)
   
    character = Character(name, meshes = meshes)
    print("Success to load GLTF!")

    return character


def load_gltf_mesh(file_path,gltf):

    meshes = []
    textures = []

    glb_data = None
    folder_path = os.path.dirname(file_path) + "/"
    file_ext = file_path.split('.')[-1]

    if file_ext == "glb":
        with open(file_path, 'rb') as f:
            glb_data = f.read()
            
    for image in gltf.images:
        textures.append(folder_path + image.uri)

    color = (200, 200, 200, 255) # for mixamo joint
    for mesh in gltf.meshes:
        vertices = []
        normals = []
        uvs = []
        indices = []
        joints = []
        weights = []
        texture_id = None
        for primitive in mesh.primitives:
            if primitive.attributes.POSITION is not None:
                accessor = gltf.accessors[primitive.attributes.POSITION]
                bufferView = gltf.bufferViews[accessor.bufferView]
                buffer = get_buffer_data(file_path, gltf,bufferView,glb_data)

                buffer_data = np.frombuffer(buffer, dtype=np.float32, count=accessor.count * 3)
                # buffer_data = buffer_data.reshape(accessor.count, 3)

                vertices.extend(buffer_data.tolist())

            if primitive.attributes.NORMAL is not None:
                accessor = gltf.accessors[primitive.attributes.NORMAL]
                bufferView = gltf.bufferViews[accessor.bufferView]
                buffer = get_buffer_data(file_path, gltf,bufferView,glb_data)

                buffer_data = np.frombuffer(buffer, dtype=np.float32, count=accessor.count * 3)
                # buffer_data = buffer_data.reshape(accessor.count, 3)

                normals.extend(buffer_data.tolist())

            if primitive.attributes.TEXCOORD_0 is not None:
                accessor = gltf.accessors[primitive.attributes.TEXCOORD_0]
                bufferView = gltf.bufferViews[accessor.bufferView]
                buffer = get_buffer_data(file_path, gltf,bufferView,glb_data)

                buffer_data = np.frombuffer(buffer, dtype=np.float32, count=accessor.count * 2)
                # buffer_data = buffer_data.reshape(accessor.count, 2)

                uvs.extend(buffer_data.tolist())

            if primitive.indices is not None:
                accessor = gltf.accessors[primitive.indices]
                bufferView = gltf.bufferViews[accessor.bufferView]
                buffer = get_buffer_data(file_path, gltf,bufferView,glb_data)

                buffer_data = np.frombuffer(buffer, dtype=np.uint16, count=accessor.count)
                indices.extend(buffer_data.tolist())

            # if primitive.attributes.JOINTS_0 is not None:
            #     accessor = gltf.accessors[primitive.attributes.JOINTS_0]
            #     bufferView = gltf.bufferViews[accessor.bufferView]
            #     buffer = get_buffer_data(file_path, gltf, bufferView, glb_data)
            #     data = np.frombuffer(buffer, dtype=np.uint16, count=accessor.count * 4, offset=accessor.byteOffset)
            #     data = data.reshape(accessor.count, 4)
            #     joints.extend(data.tolist())

            # if primitive.attributes.WEIGHTS_0 is not None:
            #     accessor = gltf.accessors[primitive.attributes.WEIGHTS_0]
            #     bufferView = gltf.bufferViews[accessor.bufferView]
            #     buffer = get_buffer_data(file_path, gltf, bufferView, glb_data)
            #     data = np.frombuffer(buffer, dtype=np.float32, count=accessor.count * 4)
            #     data = data.reshape(accessor.count, 4)
            #     weights.extend(data.tolist())

            texture_id = primitive.material

        if len(normals) == 0:
            normals = mathutil.compute_normal(vertices, indices)
        mesh = Object(mesh_type=MeshType.Custom,
                      mesh_info={"vertices":vertices, 
                                 "normals":normals,
                                "uvs":uvs,
                                "indices":indices,
                                "joint_indices" : np.array(joints),
                                "skin_weight": np.array(weights)})
        
        mesh.set_color(color)
        color = tuple(c // 2 for c in color) # For mixamo body
        if texture_id < len(textures) :
            mesh.texture_id = texture_id
            mesh.set_texture(textures[texture_id])
        meshes.append(mesh)

    return meshes

def load_gltf_joint(folder_path, gltf):
    joints = []
    inverse_bind_matrices = []

    # Extract skin and joint data
    for skin in gltf.skins:
        for joint_index in skin.joints:
            joint = gltf.nodes[joint_index]
            joints.append(joint)

        accessor = gltf.accessors[skin.inverseBindMatrices]
        bufferView = gltf.bufferViews[accessor.bufferView]

        buffer = get_buffer_data(folder_path, gltf,bufferView)

        buffer_data = np.frombuffer(buffer, dtype=np.float32, count=accessor.count * 16)
        buffer_data = buffer_data.reshape(accessor.count, 4, 4)

        inverse_bind_matrices.extend(buffer_data.tolist())
    
    # quat_rotations = Quaternions.from_euler(np.radians(rotations), order=order, world=world)

    # return (Animation(quat_rotations, positions, orients, offsets, parents), names, frametime)
    return joints, inverse_bind_matrices

def load_bvh(filepath):
    if not os.path.exists(filepath):
        return None
    
    ext = filepath.split('.')[-1]
    name = filepath.split('/')[-1]
    if ext == "bvh":
        data = BVH.load(filepath)
        joints = create_joint(data[0], data[1],scale_joint = 5.0)
        character = Character(name, joints = joints, scale_link = 5.0)
        print("BVH load success.")

        data={}

        return character

def create_joint(data,names,scale_joint):
    joints = []

    # self.rotations = data.rotations
    # self.positions = data.positions
    # self.orients = data.orients
    # self.offsets = data.offsets
    # self.parents = data.parents

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

def get_buffer_data(file_path, gltf,buffer_view, glb_data = None):
    folder_path = os.path.dirname(file_path) + "/"
    file_ext = file_path.split('.')[-1]
    buffer = gltf.buffers[buffer_view.buffer]

    if file_ext == "glb":
        return glb_data[buffer_view.byteOffset:buffer_view.byteOffset + buffer_view.byteLength]

    elif file_ext == "gltf":
        if buffer.uri.startswith('data:'):
            # Handle base64-encoded buffer
            header, encoded = buffer.uri.split(',', 1)
            data = base64.b64decode(encoded)
        else:
            # Handle external buffer
            with open(folder_path + buffer.uri, 'rb') as f:
                data = f.read()
        return data[buffer_view.byteOffset:buffer_view.byteOffset + buffer_view.byteLength]

    else:
        return None