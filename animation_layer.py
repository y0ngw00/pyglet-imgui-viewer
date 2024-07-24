import numpy as np

from object import Joint
from motionutils.Quaternions import Quaternions

class AnimationLayer:
    def __init__(self, joint):
        self.joint = joint
        self.rotations = []
        self.positions = []
        
        self.frame_start = 0
        self.frame_end = 0
        
    def animate(self, frame):
        if frame < self.frame_start or frame > self.frame_end:
            return
        
        index = frame - self.frame_start
        
        m = np.eye(4, dtype=np.float32)
        m[0:3, 0:3] = Quaternions(self.rotations[index]).transforms()[0]
        if self.joint.is_root is True:
            m[3, 0:3] = self.positions[index]
        else:
            m[3, 0:3] = self.joint.transform[3, 0:3]

        self.joint.set_transform(m)
