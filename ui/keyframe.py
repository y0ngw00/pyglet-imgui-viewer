

class KeyFrameAnimation:
    def __init__(self):
        self.keyframes = []

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
    
    def get_nearest_keyframe(self, frame):
        if frame <= self.keyframes[0].frame:
            return 0, 0
        elif frame >= self.keyframes[-1].frame:
            return len(self.keyframes) - 1, len(self.keyframes) - 1
        else:
            for i in range(len(self.keyframes) - 1):
                if self.keyframes[i].frame <= frame < self.keyframes[i + 1].frame:
                    break
            return i, i+1

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

            # Interpolate the position
            t = (frame - self.keyframes[i].frame) / (self.keyframes[i + 1].frame - self.keyframes[i].frame)
            position = [self_pos * (1 - t) + other_pos * t for self_pos, other_pos in zip(self.keyframes[i].position, self.keyframes[i + 1].position)]

        return position

class KeyFrame:
    def __init__(self, frame, position):
        self.frame = frame
        self.position = position

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
