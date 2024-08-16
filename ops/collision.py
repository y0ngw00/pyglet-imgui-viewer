import numpy as np


class CollisionHandler:
    def __init__(self, radius = 20, safe_distance = 10):
        self.rad_sq = radius ** 2
        self.radius = radius
        self.safe_distance = safe_distance
    
    def handle_collision(self, positions):
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