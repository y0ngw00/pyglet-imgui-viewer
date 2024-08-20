
import copy

class InterpolationType:
    """
    Represents the type of interpolation for keyframe animation.
    """
    LINEAR = 0
    STEP = 1
    CUBIC = 2
    BEZIER = 3
class KeyFrameAnimation:
    def __init__(self, interpolation_type=InterpolationType.LINEAR):
        self.keyframes = []
        self.interpolation_type = interpolation_type

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

    def interpolate_position(self, frame):
        if len(self.keyframes) == 0:
            raise ValueError("No keyframes")
        
        if frame <= self.keyframes[0].frame:
            position = self.keyframes[0].position
        elif frame >= self.keyframes[-1].frame:
            position = self.keyframes[-1].position
        else:
             # Find the two keyframes that the frame is between
            for i in range(len(self.keyframes) - 1):
                if self.keyframes[i].frame <= frame < self.keyframes[i + 1].frame:
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
                case _:
                    raise ValueError("Interpolation type not supported")

        return position

class KeyFrame:
    def __init__(self, frame, position):
        self.frame = frame
        self.position = copy.deepcopy(position)

    def __eq__(self, other):
        if isinstance(other, KeyFrame):
            return self.frame == other.frame
        elif isinstance(other, int):
            return self.frame == other
        else:
            raise ValueError("Unsupported operand type for <: '{}' and '{}'".format(type(self), type(other)))
        
    def __lt__(self, other):
        if isinstance(other, KeyFrame):
            return self.frame < other.frame
        elif isinstance(other, int):
            return self.frame < other
        else:
            raise TypeError("Unsupported operand type for <: '{}' and '{}'".format(type(self), type(other)))

    def __gt__(self, other):
        if isinstance(other, KeyFrame):
            return self.frame > other.frame
        elif isinstance(other, int):
            return self.frame > other
        else:
            raise TypeError("Unsupported operand type for >: '{}' and '{}'".format(type(self), type(other)))
