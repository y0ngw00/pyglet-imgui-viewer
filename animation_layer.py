import numpy as np

from motionutils.Quaternions import Quaternions

class AnimationLayer:
    def __init__(self):
        self.animations = []
        
    def add_animation(self, animation):
        self.animations.append(animation)
        
    def clear(self):
        self.animations = []
        
    def remove(self, animation):
        self.animations.remove(animation)
        
    def get_all_animations(self):
        return self.animations

    def animate(self, frame):
        for animation in self.animations:
            animation.animate(frame)
            
    def update_play_region(self, idx, frame_start, frame_end):
        self.animations[idx].update_play_region(frame_start, frame_end)
        
    def translate_region(self, idx, dx):
        self.animations[idx].translate_region(dx)
            
    def translate(self, pos):
        for anim in self.animations:
            anim.translate_position(pos)
            
    def __len__(self):
        return len(self.animations)
    
    def __getitem__(self, index):
        if len(self.animations) <= index:
            raise ValueError("Index out of range")
        return self.animations[index]