import numpy as np

from object import Joint
from motionutils.Quaternions import Quaternions

class AnimationLayer:
    def __init__(self, joint):
        self.joint = joint
        self.rotations = []
        self.positions = []
        
        self.frame_full_region_start = 0
        self.frame_full_region_end = 0
        
        self.frame_play_region_start = 0
        self.frame_play_region_end = 0
        
        self.animation_length = 0
        
    def animate(self, frame):
        if frame < self.frame_play_region_start or frame > self.frame_play_region_end:
            return
        
        index = (frame - self.frame_full_region_start) % self.animation_length
        
        m = np.eye(4, dtype=np.float32)
        m[0:3, 0:3] = Quaternions(self.rotations[index]).transforms()[0]
        if self.joint.is_root is True:
            m[3, 0:3] = self.positions[index]
        else:
            m[3, 0:3] = self.joint.transform[3, 0:3]

        self.joint.set_transform(m)
        
    def translate_position(self, pos):
        self.positions = [p + pos for p in self.positions] 
        
    def initialize_region(self, frame_start, frame_end):
        self.frame_full_region_start = frame_start
        self.frame_full_region_end = frame_end
        
        self.frame_play_region_start = frame_start
        self.frame_play_region_end = frame_end
        
        self.animation_length = frame_end - frame_start + 1
        
    def translate_region(self, dx):
        self.frame_full_region_start += dx
        self.frame_full_region_end += dx
        self.frame_play_region_start += dx
        self.frame_play_region_end += dx
                
    def update_full_region(self, frame_start, frame_end):
        self.frame_full_region_start = frame_start
        self.frame_full_region_end = frame_end
        
    def update_play_region(self, frame_start, frame_end):
        self.frame_play_region_start = frame_start
        self.frame_play_region_end = frame_end
