import numpy as np

from keyframe import KeyFrame
from enum_list import SamplingType

class Formation:
    def __init__(self, dancers, dancer_positions,boundary_points,  frame, formation_sampling = SamplingType.BOUNDARY) -> None:
        self.dancers = dancers
        self.dancer_positions = dancer_positions
        self.boundary_points = boundary_points
        self.formation_sampling = formation_sampling
        self.__frame = frame
        
            
    @property        
    def frame(self):
        return self.__frame
    
    @frame.setter
    def frame(self, frame):
        self.__frame = frame
    

            
    
    
    
# save_current_formation

# reorganize_formation

# add or delete dancer