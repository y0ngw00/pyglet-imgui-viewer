import numpy as np

from object import Joint
from motionutils.Quaternions import Quaternions

class AnimationLayer:
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
        if self.joint.is_root is True and len(self.positions) > index:
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
