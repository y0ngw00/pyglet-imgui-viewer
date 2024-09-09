import base64
import os
import random
import json
import time
from copy import deepcopy

import numpy as np
from pygltflib import GLTF2, Node, Skin, Accessor, BufferView, BufferFormat
import pickle as pkl

from motionutils import BVH
from motionutils.Quaternions import Quaternions
from object import Object,MeshType,Character,Joint,Link
from animation_layer import AnimationLayer
from extern_file_parser import pycomcon
import mathutil
from utils import smpl2fbx, export_animated_mesh, process_mesh_info
import transforms
import torch
from test import synthesize

sample_character_path = "./data/SMPL_m_unityDoubleBlends_lbs_10_scale5_207_v1.0.0.fbx"
sample_texture_path = "./data/m_01_alb.002.png"
sample_character = None

bone_name_from_index = {
    0 : 'Pelvis',
    1 : 'L_Hip',
    2 : 'R_Hip',
    3 : 'Spine1',
    4 : 'L_Knee',
    5 : 'R_Knee',
    6 : 'Spine2',
    7 : 'L_Ankle',
    8: 'R_Ankle',
    9: 'Spine3',
    10: 'L_Foot',
    11: 'R_Foot',
    12: 'Neck',
    13: 'L_Collar',
    14: 'R_Collar',
    15: 'Head',
    16: 'L_Shoulder',
    17: 'R_Shoulder',
    18: 'L_Elbow',
    19: 'R_Elbow',
    20: 'L_Wrist',
    21: 'R_Wrist',
    22: 'L_Hand',
    23: 'R_Hand'
}

bone_index_from_name = {
    'Pelvis': 0,
    'L_Hip' : 1,
    'R_Hip' : 2,
    'Spine1': 3,
    'L_Knee': 4,
    'R_Knee': 5,
    'Spine2': 6,
    'L_Ankle': 7,
    'R_Ankle': 8,
    'Spine3': 9,
    'L_Foot': 10,
    'R_Foot': 11,
    'Neck': 12,
    'L_Collar': 13,
    'R_Collar': 14,
    'Head': 15,
    'L_Shoulder': 16,
    'R_Shoulder': 17,
    'L_Elbow': 18,
    'R_Elbow': 19,
    'L_Wrist': 20,
    'R_Wrist': 21,
    'L_Hand': 22,
    'R_Hand': 23
}


def load_gltf(filename):
    gltf = GLTF2().load(filename)
    name = filename.split('/')[-1]
    
    file_ext = filename.split('.')[-1]
    glb_data = None
    if file_ext == "glb":
        with open(filename, 'rb') as f:
            glb_data = f.read()
    meshes = load_gltf_mesh(filename, gltf,glb_data)

    joints = load_gltf_joint(filename, gltf,glb_data)
   
    character = Character(name, meshes = meshes, scale=[100,100,100])
    print("Success to load GLTF!")

    return character


def load_gltf_mesh(file_path,gltf,glb_data=None):

    meshes = []
    textures = []

    folder_path = os.path.dirname(file_path) + "/"
            
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
       
        for primitive in mesh.primitives:
            if primitive.attributes.POSITION is not None:
                vertex_accessor = gltf.accessors[primitive.attributes.POSITION]
                bufferView = gltf.bufferViews[vertex_accessor.bufferView]
                # buffer = glb_data[bufferView.byteOffset:bufferView.byteOffset + bufferView.byteLength]

                buffer = get_buffer_data(file_path, gltf,bufferView,glb_data)
                buffer_data = np.frombuffer(buffer, dtype=np.float32, count=vertex_accessor.count * 3)
                # buffer_data = buffer_data.reshape(accessor.count, 3)

                vertices.extend(buffer_data.tolist())

            if primitive.attributes.NORMAL is not None:
                normal_accessor = gltf.accessors[primitive.attributes.NORMAL]
                bufferView = gltf.bufferViews[normal_accessor.bufferView]
                buffer = get_buffer_data(file_path, gltf,bufferView,glb_data)

                buffer_data = np.frombuffer(buffer, dtype=np.float32, count=normal_accessor.count * 3)
                # buffer_data = buffer_data.reshape(accessor.count, 3)

                normals.extend(buffer_data.tolist())

            if primitive.attributes.TEXCOORD_0 is not None:
                uvs_accessor = gltf.accessors[primitive.attributes.TEXCOORD_0]
                bufferView = gltf.bufferViews[uvs_accessor.bufferView]
                buffer = get_buffer_data(file_path, gltf,bufferView,glb_data)

                buffer_data = np.frombuffer(buffer, dtype=np.float32, count=uvs_accessor.count * 2)
                # buffer_data = buffer_data.reshape(accessor.count, 2)

                uvs.extend(buffer_data.tolist())

            if primitive.indices is not None:
                accessor = gltf.accessors[primitive.indices]
                bufferView = gltf.bufferViews[accessor.bufferView]
                buffer = get_buffer_data(file_path, gltf,bufferView,glb_data)

                buffer_data = np.frombuffer(buffer, dtype=np.uint16, count=accessor.count)
                indices.extend(buffer_data.tolist())

            # if primitive.attributes.WEIGHTS_0 is not None and primitive.attributes.JOINTS_0 is not None:
            #     weights_accessor = gltf.accessors[primitive.attributes.WEIGHTS_0]
            #     bufferView = gltf.bufferViews[weights_accessor.bufferView]
            #     # weights_buffer = gltf.buffers[bufferView.buffer]
            #     weights_buffer = get_buffer_data(file_path, gltf, bufferView, glb_data)
            #     weights_data = np.frombuffer(weights_buffer, dtype=np.float32,count=weights_accessor.count * 4, offset=weights_accessor.byteOffset)
            #     weights_data = weights_data.reshape(weights_accessor.count, 4)
            #     weights.extend(weights_data.tolist())
                
            #     joints_accessor = gltf.accessors[primitive.attributes.JOINTS_0]
            #     bufferView = gltf.bufferViews[joints_accessor.bufferView]
            #     joints_buffer = get_buffer_data(file_path, gltf, bufferView, glb_data)
            #     joints_data = np.frombuffer(joints_buffer, dtype=np.uint8, count=joints_accessor.count * 4, offset=joints_accessor.byteOffset)
            #     joints_data = joints_data.reshape(joints_accessor.count, 4)
            #     joints.extend(joints_data.tolist())


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

def load_gltf_joint(folder_path, gltf,glb_data):
    joints = []
    inverse_bind_matrices = []

    # Extract skin and joint data
    for skin in gltf.skins:
        for joint_index in skin.joints:
            joint = gltf.nodes[joint_index]
            joints.append(joint)

        accessor = gltf.accessors[skin.inverseBindMatrices]
        bufferView = gltf.bufferViews[accessor.bufferView]

        buffer = get_buffer_data(folder_path, gltf,bufferView,glb_data)

        buffer_data = np.frombuffer(buffer, dtype=np.float32, count=accessor.count * 16)
        buffer_data = buffer_data.reshape(accessor.count, 4, 4)

        inverse_bind_matrices.extend(buffer_data.tolist())
    
    # quat_rotations = Quaternions.from_euler(np.radians(rotations), order=order, world=world)

    # return (Animation(quat_rotations, positions, orients, offsets, parents), names, frametime)
    return joints, inverse_bind_matrices

def load_smpl_fbx(filename):
    vertices, normals, uvs, indices = process_mesh_info(filename)
    mesh = Object(mesh_type=MeshType.Custom,
                      mesh_info={"vertices":vertices, 
                                 "normals":normals,
                                "uvs":uvs,
                                "indices":indices,
                                })
    mesh.mesh.stride = 3 # set to triangular mesh
    
    fbx_loader = pycomcon.FBXLoader()
    loadResult = fbx_loader.load_fbx(filename)
    name = filename.split('/')[-1]
    joints = load_fbx_joint(fbx_loader, False)
    
    character = Character(name, meshes = [mesh],joints = joints, scale=[1,1,1]) 
    return character 

def load_fbx(filename, load_anim = False):
    fbx_loader = pycomcon.FBXLoader()
    loadResult = fbx_loader.load_fbx(filename)
    name = filename.split('/')[-1]

    meshes = load_fbx_mesh(fbx_loader)
    # if len(meshes) > 0:
        # meshes[0].set_color((0, 4, 47, 255))
        # meshes[1].set_color((200, 200, 200, 255))
    joints = load_fbx_joint(fbx_loader, load_anim)

    character = Character(name, meshes = meshes,joints = joints, scale=[1,1,1])
    
    # Exception only for SMPL model. Set root joint to the Pelvis joint instead of root joint.
    if "SMPL" in name or "smpl" in name: 
        character.redefinite_root(1)
    print("Success to load FBX!")
    return character

def load_fbx_mesh(fbx_loader):
    meshes = []
    
    fbx_meshes = fbx_loader.get_meshes()
    
    for fbx_mesh in fbx_meshes:
        vertices = fbx_mesh.vertices
        normals = fbx_mesh.normals
        uvs = fbx_mesh.texCoords
        indices = fbx_mesh.indices
                   
        skin_data = np.array(fbx_mesh.skinData)    
        if skin_data is None:
            mesh = Object(mesh_type=MeshType.Custom,
                      mesh_info={"vertices":vertices, 
                                 "normals":normals,
                                "uvs":uvs,
                                "indices":indices,
                                })
        else:
            mesh = Object(mesh_type=MeshType.Custom,
                      mesh_info={"vertices":vertices, 
                                 "normals":normals,
                                "uvs":uvs,
                                "indices":indices,
                                "skin_data" : skin_data,
                                })
            
        # diffuse_map = fbx_mesh.diffuseTexture
        # diffuse_map = "/home/imo/Downloads/SMPLitex-texture-00000.png"
        diffuse_map = "/home/imo/Downloads/m_01_alb.002.png"
        # diffuse_map = sample_texture_path
        # diffuse_map = "/home/imo/Project/DanceTransfer/data/mixamo_library/Amy.fbm/Ch46_1001_Diffuse.png"
        if diffuse_map != '':
            mesh.set_texture(diffuse_map)
        
        mesh.mesh.stride = 3 # set to triangular mesh            
        meshes.append(mesh)
        
    # if diffuse_map == '':
    if len(meshes) >= 2:
        meshes[1].set_color((200, 200, 200, 255))
        meshes[0].set_color((0, 4, 47, 255))
    
    return meshes

def load_fbx_joint(fbx_loader, load_anim):
    joints = []
    fbx_joints = fbx_loader.get_joints()
    
    for fbx_joint in fbx_joints:
        name = fbx_joint.name             
        joint = Joint(name,5.0)

        parent_idx = fbx_joint.parentIndex
        transform = fbx_joint.transform 
        joint.init_transform_inv = fbx_joint.invBindPose
        if joint.init_transform_inv.shape[0] == 0:
            joint.init_transform_inv = np.eye(4, dtype=np.float32)

        if parent_idx == -1:
            joint.set_root(True)
        else:
            joint.set_parent(joints[parent_idx])
        # joint.set_position(transform[3,0:3])
        joint.set_transform(transform)
        joint.parent_index = parent_idx

                    
        animation_data =  None
        if load_anim is True:
            animation_data = fbx_joint.animList
            animation_data = np.array(animation_data)

            if animation_data is not None and len(animation_data) > 0:
                rot_mat = animation_data[:,:3,:3]
                rot_quat = Quaternions.from_transforms(rot_mat).qs
                
                anim_layer = AnimationLayer(joint)
                anim_layer.rotations = list(rot_quat)
                # if parent_idx ==-1:
                anim_layer.positions = list(animation_data[:,3,0:3])
                anim_layer.initialize_region(0, len(animation_data) - 1)
                
                joint.anim_layers.append(anim_layer)            
        joints.append(joint)

    return joints

def load_fbx_animation(filepath):
    if not os.path.exists(filepath):
        return None
    
    fbx_loader = pycomcon.FBXLoader()
    loadResult = fbx_loader.load_fbx(filepath)
    name = filepath.split('/')[-1]
    
    joints = load_fbx_joint(fbx_loader, load_anim = True)
    return name, joints

def load_bvh(filepath, scale = [1.0,1.0,1.0]):
    if not os.path.exists(filepath):
        return None
    
    ext = filepath.split('.')[-1]
    name = filepath.split('/')[-1]
    if ext != "bvh":
        print("This file is not BVH format. Please check the file extension.")
        return None
        
    data = BVH.load(filepath)
    joints = create_bvh_joint(data[0], data[1],scale_joint = 5.0)
    character = Character(name, joints = joints,scale=scale, scale_link = 5.0)
    print("BVH load success.")

    data={}

    return character


def load_bvh_animation(filepath):
    if not os.path.exists(filepath):
        return None
    
    ext = filepath.split('.')[-1]
    name = filepath.split('/')[-1]
    if ext != "bvh":
        print("This file is not BVH format. Please check the file extension.")
        return None
        
    data = BVH.load(filepath)
    joints = create_bvh_joint(data[0], data[1],scale_joint = 5.0)
    
    print("BVH load success.")

    return name, joints

def create_sample_character():
    global sample_character
    if sample_character is None:
        sample_character = load_fbx(sample_character_path)
        return sample_character
    return sample_character.copy()
    

def save_smpl_fbx(pkl_path, fbx_path):
    startTime = time.perf_counter()

    if pkl_path.endswith('.pkl'):
        if not os.path.isfile(pkl_path):
            print('ERROR: Invalid input file')
            return

        poses_processed = smpl2fbx(
            input_path=pkl_path,
            gender='male',
            fps_source=30,
            fps_target=30,
            start_origin=0,
            person_id=0
        )
        export_animated_mesh(fbx_path)

    print('--------------------------------------------------')
    print('Animation export finished.')
    print(f'Poses processed: {str(poses_processed)}')
    print(f'Processing time : {time.perf_counter() - startTime:.2f} s')
    print('--------------------------------------------------')
    return

def create_bvh_joint(data,names,scale_joint):
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
        joint.parent_index = data.parents[idx]
        
        anim_layer = AnimationLayer(joint)
        anim_layer.initialize_region(0, len(data.rotations) - 1)
        joint.anim_layers.append(anim_layer)  
        joints.append(joint)  
       
    for frame, rot in enumerate(data.rotations):
        for idx, joint in enumerate(joints):
            rotation = rot[idx]
            rotation[1:] *= -1 # Because I use row-major matrix....sorry
            joint.anim_layers[-1].rotations.append(rotation)
            if joint.is_root is True:
                joint.anim_layers[-1].positions.append(data.positions[frame][idx])

    return joints

def get_buffer_data(file_path, gltf,buffer_view, glb_data=None):
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

def generate_motion_from_network(character,condition,audio_path, network_path,output_path, nframe,  load_translation = True):
    synthesize(condition, audio_path, network_path, output_path,nframe)
    load_pose_from_pkl(output_path+"output.pkl", character, 0, use_translation=load_translation)
        

def load_pose_from_pkl(pose_dir, character, character_idx, use_translation=True):
    load_translation = False
    with open(pose_dir, "rb") as f:
        seq_data = pkl.load(f)
        
    smpl_poses = seq_data["smpl_poses"] #shape (n_persons, n_frames, pose_dim) , smpl pose excluding L/R hand joint
    if smpl_poses.shape[-1]<23*3:
        smpl_poses = np.concatenate([smpl_poses, np.zeros(list(smpl_poses.shape[:-1]) + [23*3 -smpl_poses.shape[-1] ])], axis=-1)
    if "smpl_orients" in seq_data:
        smpl_orients = seq_data["smpl_orients"]
        smpl_poses = np.concatenate([smpl_orients, smpl_poses], axis=-1)            
    if "root_trans" in seq_data and use_translation is True:
        smpl_trans = seq_data["root_trans"]
        load_translation = True
    
    if "meta" in seq_data:
        metadata = seq_data["meta"]
                
        orig_start, orig_end = metadata["orig_start"], metadata["orig_end"]
        orig_seq_len = smpl_poses.shape[1]  # actual sequence length
                
    smpl_poses = torch.from_numpy(smpl_poses)
    n_persons, seq_len = smpl_poses.shape[:2]
    if character_idx >= n_persons:
        return
    smpl_poses = smpl_poses.view(n_persons, seq_len, -1, 3)  # reshape to (n_persons, seq_len, J, 3)

    smpl_poses = transforms.aa2quat(smpl_poses)

    ret = smpl_poses[character_idx].detach().cpu().numpy()

    positions = None
    if load_translation is True:
        positions = smpl_trans[character_idx] * 100.0  # convert to cm
        positions[:, 1] -= positions[0, 1]  # set the first frame to 0
        positions[:, 1] += character.get_root_position()[1]

    for idx,joint in enumerate(character.joints):
        if idx==0:
            continue
        for name in bone_index_from_name:
            if name in joint.name:
                data_index = bone_index_from_name[name]
                
        rot_quat = -Quaternions(ret[:,data_index])
        anim_layer = AnimationLayer(joint)
        anim_layer.rotations = list(rot_quat)
        if load_translation and ("Pelvis" in joint.name or "pelvis" in joint.name):
            anim_layer.positions= list(positions)

        anim_layer.initialize_region(0, len(rot_quat) - 1)
        joint.anim_layers.append(anim_layer)  
    
    print("Success to generate. data representation: ", ret.shape)
    return

def convert_joint_to_smpl_format(dancer, nframe, add_root_trajectory = True):
    character = dancer.target
    joints = character.joints[1:] if character.is_smpl is True else character.joints
    num_root_condition = 3 if add_root_trajectory is True else 1
    motion_condition = np.zeros((nframe, len(joints) * 3 +num_root_condition), dtype=np.float32)
    root_positions= np.zeros((nframe, 3), dtype=np.float32)
        
    for frame in range(nframe):
        dancer.animate(frame)
        character.update_world_transform()
        for j_idx, joint in enumerate(joints):
            rot = torch.tensor((-joint.get_rotation(frame)).qs, dtype=torch.float32)
            aa_rot = transforms.quat2aa(rot)
            if aa_rot is not [0,0,0]:
                for name in bone_index_from_name:
                    if name in joint.name:
                        data_index = bone_index_from_name[name]
                        motion_condition[frame, data_index * 3: data_index * 3 + 3] = aa_rot
                
                motion_condition[frame, -num_root_condition] = character.get_root_position()[1] * 0.01
        
        root_positions[frame] = character.get_root_position()
    
    if add_root_trajectory is True:
        root_vel = torch.from_numpy(root_positions[1:] - root_positions[:-1])
        last_diff = torch.from_numpy(root_positions[-1] - root_positions[-2])
        last_diff = last_diff.unsqueeze(0)
        root_vel = torch.cat((root_vel, last_diff), dim=0)
        
        indices = torch.tensor([0, 2]) # x,z component
        root_vel = root_vel[:, indices]
        
        
        motion_condition[:, -num_root_condition+1:] = root_vel
    return motion_condition

def write_pkl(pred_clips, dataset_info, log_dir="", name_prefix=""):
    
    translation = None
    if dataset_info["use_contact"] is True:
        pred_clips = pred_clips[:,:,:-4]
    
    if dataset_info["translation"] is True:
        xz_vel = pred_clips[:,:,-2:]
        xz_translation = torch.cumsum(xz_vel, dim=1)
        # xz_translation = np.cumsum(xz_vel, axis=1)
        pred_clips = pred_clips[:,:,:-2]
    
    y_height = pred_clips[:,:,-1]
    pred_clips = pred_clips[:,:,:-1]
        
    if dataset_info["translation"] is True:
        translation = torch.cat([xz_translation[:,:,0].unsqueeze(-1), y_height.unsqueeze(-1), xz_translation[:,:,1].unsqueeze(-1)], dim=-1)
    else:
        y_height = y_height.unsqueeze(-1)
        translation = torch.cat([torch.zeros_like(y_height), y_height, torch.zeros_like(y_height)], dim=-1)
    
    
    if dataset_info["translation"] is True:        
        data = {
            "smpl_poses": pred_clips.detach().cpu().numpy(),
            "root_trans": translation.detach().cpu().numpy(),
        }
    elif dataset_info["translation"] is False:
        data = {
            "smpl_poses": pred_clips.detach().cpu().numpy(),
        }

    # Save the data to a .pkl file
    fname = f"{log_dir}/{name_prefix}.pkl"
    with open(fname, "wb") as f:
        pkl.dump(data, f)