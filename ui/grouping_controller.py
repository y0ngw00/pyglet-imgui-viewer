import numpy as np

from keyframe_animation import KeyFrameAnimation, InterpolationType
from keyframe import KeyFrame
from animation_layer import AnimationLayer

from interface import UI

class Grouping:
    def __init__(self, dancers, group_indices, frame) -> None:
        self.dancers = dancers
        self.group_indices = group_indices
        self.__frame = frame
   
    @property        
    def frame(self):
        return self.__frame
    
    @frame.setter
    def frame(self, frame):
        self.__frame = frame
     

class GroupingController:
    def __init__(self) -> None:
        self.grouping = []
        self.anim_layer = KeyFrameAnimation(self, InterpolationType.STEP)
    
    def animate(self, frame) -> None:
        positions = None
        if len(self.anim_layer.keyframes) > 0:
            positions = self.anim_layer.interpolate_position(frame)
        
        if positions is None:
            return

        dancers = UI.get_dancers()
        for i, pos in enumerate(positions):
            dancers[i].group_index = pos
        
    
    def insert_grouping_keyframe(self, dancers, group_indices, curr_frame) -> None:
        curr_group = Grouping(dancers, group_indices, curr_frame)
                
        self.anim_layer.add_keyframe(KeyFrame(curr_frame, group_indices))
        self.anim_layer.update_play_region(0, curr_frame)         
         
        idx = 0
        for i, group in enumerate(self.grouping):
            if group.frame > curr_frame:
                idx = i
                break
        self.grouping.insert(idx, curr_group)
        
    def get_closest_grouping(self, frame) -> Grouping:
        closest_frame = 0
        closest_grouping = None
        for grouping in self.grouping:
            if grouping.frame <= frame and grouping.frame >= closest_frame:
                closest_frame = grouping.frame
                closest_grouping = grouping
                
        return closest_grouping
        
    def clear(self):
        self.__init__()
