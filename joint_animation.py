import numpy as np

from motionutils.Quaternions import Quaternions
from copy import deepcopy
class JointAnimation:
    def __init__(self, joint):
        self.joint = joint
        self.rotations = []
        self.positions = []
        
        self.frame_original_region_start = 0
        self.frame_original_region_end = 0
        
        self.frame_play_region_start = 0
        self.frame_play_region_end = 0
        
        self.animation_length = 0
        self.animation_speed = 1.0
        
    def animate(self, frame):
        frame_end = self.frame_play_region_start + (self.frame_play_region_end - self.frame_play_region_start)/self.animation_speed
        if frame < self.frame_play_region_start or frame > frame_end:
            return
        
        index = int((frame - self.frame_original_region_start) * self.animation_speed) % self.animation_length
        
        m = np.eye(4, dtype=np.float32)
        m[0:3, 0:3] = Quaternions(self.rotations[index]).transforms()[0]
        if len(self.positions) > index:
            m[3, 0:3] = self.positions[index]
        else:
            m[3, 0:3] = self.joint.transform[3, 0:3]

        self.joint.set_transform(m)
        
    @property
    def get_animation_speed(self):
        return self.animation_speed
    
    @get_animation_speed.setter
    def set_animation_speed(self, speed):
        self.animation_speed = speed
                
    def get_rotation_quaternion(self, frame):
        if frame < self.frame_play_region_start or frame > self.frame_play_region_end:
            return None
        
        index = (frame - self.frame_original_region_start) % self.animation_length
        return Quaternions(self.rotations[index])
         
    def get_play_region(self):
        return self.frame_play_region_start, self.frame_play_region_end
    
    def translate_position(self, pos):
        self.positions = [p + pos for p in self.positions] 
        
    def initialize_region(self, frame_start, frame_end):
        self.frame_original_region_start = frame_start
        self.frame_original_region_end = frame_end
        
        self.frame_play_region_start = frame_start
        self.frame_play_region_end = frame_end
        
        self.animation_length = frame_end - frame_start + 1
        
    def translate_region(self, dx):
        self.frame_original_region_start += dx
        self.frame_original_region_end += dx
        self.frame_play_region_start += dx
        self.frame_play_region_end += dx
                
    def update_full_region(self, frame_start, frame_end):
        self.frame_original_region_start = frame_start
        self.frame_original_region_end = frame_end
        
    def update_play_region(self, frame_start, frame_end):
        self.frame_play_region_start = frame_start
        self.frame_play_region_end = frame_end
        
    @classmethod
    def create_mirrored_animation(cls, joint_anim):
        new_anim = cls(joint_anim.joint)
        new_anim.rotations = deepcopy(joint_anim.rotations)
        new_anim.positions = deepcopy(joint_anim.positions)
        new_anim.initialize_region(joint_anim.frame_original_region_start, joint_anim.frame_original_region_end)
        new_anim.rotations[:,2:] = new_anim.rotations[:,2:] * -1
        new_anim.positions[:,0] = -new_anim.positions[:,0]
            
        return new_anim
