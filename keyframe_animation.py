class InterpolationType:
    """
    Represents the type of interpolation for keyframe animation.
    """
    LINEAR = 0
    STEP = 1
    CUBIC = 2
    BEZIER = 3
class KeyFrameAnimation:
    def __init__(self, target, interpolation_type=InterpolationType.LINEAR):
        self.target = target
        self.keyframes = []
        self.interpolation_type = interpolation_type
        self.current_keyframe_idx = 0

        self.frame_original_region_start = 0
        self.frame_original_region_end = 0
        self.frame_play_region_start = 0
        self.frame_play_region_end = 0
        
        self.animation_speed = 1.0
        
    @property
    def animation_length(self):
        return len(self.keyframes)
    
    def initialize_region(self, frame_start, frame_end):
        self.frame_original_region_start = frame_start
        self.frame_original_region_end = frame_end
        
        self.frame_play_region_start = frame_start
        self.frame_play_region_end = frame_end
    
    def update_play_region(self, frame_start, frame_end, bTrim = True):
        self.frame_play_region_start = frame_start
        self.frame_play_region_end = frame_end
        if bTrim is not True:
            original_length = self.frame_original_region_end - self.frame_original_region_start
            play_length = self.frame_play_region_end - self.frame_play_region_start
            self.animation_speed = original_length / play_length

    def add_keyframe(self, keyframe):
        if len(self.keyframes) == 0:
            self.keyframes.append(keyframe)
            return
        
        for i, kf in enumerate(self.keyframes):
            if keyframe<kf:
                self.keyframes.insert(i, keyframe)
                return
            elif keyframe==kf:
                self.keyframes[i] = keyframe
                return
        
        self.keyframes.append(keyframe)
        return
    
    def clear_keyframe(self):
        self.keyframes = []
    
    def get_nearest_keyframe(self, frame):
        if len(self.keyframes) == 1 or frame < self.keyframes[0].frame:
            return 0, 0
        elif frame > self.keyframes[-1].frame:
            return self.keyframes[-1].frame, self.keyframes[-1].frame
        else:
            idx = 0
            for i in range(len(self.keyframes) - 1):
                if frame >= self.keyframes[i].frame and frame <= self.keyframes[i + 1].frame:
                    idx = i
                    break
            return self.keyframes[idx].frame, self.keyframes[idx+1].frame

    def animate(self, frame):
        if frame < self.frame_play_region_start or frame > self.frame_play_region_end:
            return
        position = self.interpolate_position(frame)
        if self.target is not None:
            self.target.set_position(position)
        
    def interpolate_position(self, frame):
        if len(self.keyframes) == 0:
            raise ValueError("No keyframes")            

        frame = (frame - self.frame_play_region_start) * self.animation_speed + self.frame_original_region_start
        
        if frame <= self.keyframes[0].frame:
            position = self.keyframes[0].position
            self.current_keyframe_idx = 0
        elif frame >= self.keyframes[-1].frame:
            position = self.keyframes[-1].position
            self.current_keyframe_idx = len(self.keyframes) - 1
        else:
             # Find the two keyframes that the frame is between
            if frame >= self.keyframes[self.current_keyframe_idx].frame:
                for i in range(self.current_keyframe_idx, len(self.keyframes) - 1):
                    if self.keyframes[i].frame <= frame and frame < self.keyframes[i + 1].frame:
                        self.current_keyframe_idx = i
                        break
            elif frame < self.keyframes[self.current_keyframe_idx].frame:
                for i in range(0, self.current_keyframe_idx):
                    if self.keyframes[i].frame <= frame and frame < self.keyframes[i + 1].frame:
                        self.current_keyframe_idx = i
                        break
            else:
                raise ValueError("Frame is not valid")

            match self.interpolation_type:
                case InterpolationType.LINEAR:
                    # Interpolate the position
                    t = (frame - self.keyframes[i].frame) / (self.keyframes[i + 1].frame - self.keyframes[i].frame)
                    position = [self_pos * (1 - t) + other_pos * t for self_pos, other_pos in zip(self.keyframes[i].position, self.keyframes[i + 1].position)]

                case InterpolationType.STEP:
                    position = self.keyframes[i].position
                    
                case InterpolationType.CUBIC:
                    # Interpolate the position
                    t = (frame - self.keyframes[i].frame) / (self.keyframes[i + 1].frame - self.keyframes[i].frame)
                    position = [self_pos * (1 - t) + other_pos * t for self_pos, other_pos in zip(self.keyframes[i].position, self.keyframes[i + 1].position)]
                case _:
                    raise ValueError("Interpolation type not supported")
        
        return position
    
    def translate_region(self, dx):
        self.frame_play_region_start += dx
        self.frame_play_region_end += dx
