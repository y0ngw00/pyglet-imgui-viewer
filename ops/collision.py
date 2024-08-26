import numpy as np
from keyframe import KeyFrame

class CollisionHandler:
    def __init__(self, radius = 20, n_knot = 1, safe_distance = 10):
        self.radius = radius
        self.n_knot = n_knot
        self.safe_distance = safe_distance
        
    def handle_collision(self, dancers, min_frame, max_frame):
        pos_diffs = np.zeros((max_frame-min_frame+1, len(dancers), 3), dtype = np.float32)
        for frame in range(min_frame, max_frame+1):
            positions = []
            for i, dancer in enumerate(dancers):
                position = dancer.root_keyframe.interpolate_position(frame)
                positions.append(position)
            positions = np.array(positions)
            pos_diff = self.compute_resolved_position_diff(positions)
            pos_diffs[frame-min_frame] = pos_diff
               
        for i, dancer in enumerate(dancers):
            pos_diff = pos_diffs[:,i,:]
            pos_norm = np.linalg.norm(pos_diff, axis = 1)

            non_zero_indices = np.nonzero(pos_norm)[0]
            non_zero_values = pos_norm[non_zero_indices]
            
            min_indices = np.zeros(self.n_knot, dtype = np.int32)
            if len(non_zero_indices) == 0:
                continue
            elif len(non_zero_indices) == 1:
                min_indices = non_zero_indices
            else:
                min_indices = non_zero_indices[np.argpartition(non_zero_values, self.n_knot)[:self.n_knot]]
            
            if np.all(pos_diff == 0):
                continue
            
            positions=[]
            for idx in min_indices:
                position = dancer.root_keyframe.interpolate_position(idx+min_frame)
                positions.append(position)
            for j, idx in enumerate(min_indices):
                diff = pos_diff[idx]
                diff *= 30 / np.linalg.norm(diff)
                keyframe = KeyFrame(idx+min_frame, positions[j] + diff)
                dancer.root_keyframe.add_keyframe(keyframe)            
    
    
    def compute_resolved_position_diff(self,positions):
        posdiff_matrix, col_matrix = self.collision_matrix(positions)
        col_distance_mat = posdiff_matrix * col_matrix[..., np.newaxis]
        
        diff = np.zeros((len(positions), 3), dtype=np.float32)
        
        for idx, pos in enumerate(positions):
            if col_matrix[idx].any():
                dir = np.sum(col_distance_mat[idx], axis = 0)/2*np.sum(col_matrix[idx])
                dir *= self.safe_distance
                diff[idx,0] += (dir)[0]
                diff[idx,2] += (dir)[1]
        
        return diff
                
    
    def collision_matrix(self, positions):
        n_dancer = len(positions)
        posdiff_matrix = positions.reshape(-1, 1, positions.shape[-1]) - positions
        
        y_mask = np.ones(positions.shape[-1], dtype=bool)
        y_mask[1] = False
        
        posdiff_matrix = posdiff_matrix[..., y_mask]

        distance_matrix = np.linalg.norm(posdiff_matrix, axis=-1)
        
        col_matrix = (distance_matrix < self.radius)
        col_matrix[range(n_dancer), range(n_dancer)] = False

        # distance_matrix = np.zeros((n_dancer, n_dancer), dtype=np.float32)
        return posdiff_matrix, col_matrix