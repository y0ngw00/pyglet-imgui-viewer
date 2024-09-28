import numpy as np

from keyframe_animation import KeyFrameAnimation, InterpolationType
from keyframe import KeyFrame
from formation import Formation
from animation_layer import AnimationLayer
from ops import SocialForceModel

from interface import UI

class FormationController:
    def __init__(self) -> None:
        self.formations = []
        self.anim_layer = AnimationLayer()
        pass
    
    def animate(self, frame) -> None:
        positions = self.anim_layer.interpolate_position(frame)
        if positions is None:
            return
        
        dancers = UI.get_dancers()
        for i, pos in enumerate(positions):
            dancers[i].set_character_pos(pos)
            
    def load(self, data):
        dancers = UI.get_dancers()
        for frame, form_data in data.items():
            curr_frame = int(frame)
            prev_frame = int(form_data["prev_frame"])
            dancer_positions = form_data["dancer_positions"]
            formation_boundaries = form_data["boundary_points"]
            self.insert_formation_keyframe(dancers, dancer_positions, formation_boundaries, prev_frame, curr_frame)
    
    def save(self, name, data):
        assert len(self.formations) == len(self.anim_layer.get_all_animations())
        
        state = {}
        for anim in self.anim_layer.get_all_animations():
            formation = anim.target
            assert isinstance(formation, Formation)
            
            formation_data = formation.__dict__.copy()
            
            if "dancers" in formation_data:
                formation_data.pop("dancers")
                
            formation_data["prev_frame"] = anim.frame_play_region_start
            
            state[str(formation.frame)] = formation_data
        
        data[name] = state   
    
    
    def get_all_formation(self):
        return self.formations
     
    def compute_intermediate_positions(self,num_dancers, prev_formation, curr_formation, start_frame, end_frame) -> None:
        curr_pos = np.array(curr_formation.dancer_positions)
        prev_pos = np.array(prev_formation.dancer_positions)
        
        keyframe_anim = KeyFrameAnimation(curr_formation, InterpolationType.LINEAR)
        positions = np.zeros((num_dancers, end_frame - start_frame +1, 3), dtype = np.float32)
        
         
        for frame in range(start_frame, end_frame+1):
            t = (frame - start_frame) / (end_frame - start_frame) if end_frame != start_frame else 1
            positions[:, frame-start_frame] = prev_pos * (1 - t) + curr_pos * t
            keyframe_anim.add_keyframe(KeyFrame(frame, positions[:, frame-start_frame]))
            
        keyframe_anim.initialize_region(start_frame, end_frame)
        self.anim_layer.add_animation(keyframe_anim)
    
    def insert_formation_keyframe(self, dancers, dancer_positions,formation_boundaries, prev_frame, curr_frame) -> None:
        curr_formation = Formation(dancers, dancer_positions,formation_boundaries, curr_frame, None)
        prev_formation = self.get_closest_formation(prev_frame)
        if prev_formation is None:
            prev_formation = Formation(dancers, dancer_positions,formation_boundaries, curr_frame, None)
        
        self.compute_intermediate_positions(len(dancers),prev_formation,curr_formation, prev_frame, curr_frame)
        
        idx = 0
        for i, form in enumerate(self.formations):
            if form.frame > curr_frame:
                idx = i
                break
        self.formations.insert(idx, curr_formation)
        
    def get_formation_shift_animation(self, formation) -> KeyFrameAnimation:
        for anim in self.anim_layer.get_all_animations():
            if anim.target == formation:
                return anim
            
        raise ValueError("BUG : Corresponding animation of the formation is not found")
            
    def get_closest_formation(self, frame) -> Formation:
        closest_frame = 0
        closest_formation = None
        for formation in self.formations:
            if formation.frame <= frame and formation.frame >= closest_frame:
                closest_frame = formation.frame
                closest_formation = formation
                
        return closest_formation
    
    def clear(self):
        self.formations = []
        self.anim_layer.clear()
    
    def correct_formation(self, frame) -> None:
        

        # sim_model = SocialForceModel()
        # positions = sim_model.correct_trajectory(positions)
        return
            
            
    
    
    
# save_current_formation

# reorganize_formation

# add or delete dancer