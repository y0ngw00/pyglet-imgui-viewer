
import copy
class KeyFrame:
    def __init__(self, frame, position):
        self.__frame = frame
        self.position = copy.deepcopy(position)

    @property
    def frame(self):
        return self.__frame

    @frame.setter
    def frame(self, frame):
        if frame < 0:
            frame = 0
        self.__frame = frame
        
    def __eq__(self, other):
        if isinstance(other, KeyFrame):
            return self.__frame == other.frame
        elif isinstance(other, int):
            return self.__frame == other
        else:
            raise ValueError("Unsupported operand type for <: '{}' and '{}'".format(type(self), type(other)))
        
    def __lt__(self, other):
        if isinstance(other, KeyFrame):
            return self.__frame < other.frame
        elif isinstance(other, int):
            return self.__frame < other
        else:
            raise TypeError("Unsupported operand type for <: '{}' and '{}'".format(type(self), type(other)))

    def __gt__(self, other):
        if isinstance(other, KeyFrame):
            return self.__frame > other.frame
        elif isinstance(other, int):
            return self.__frame > other
        else:
            raise TypeError("Unsupported operand type for >: '{}' and '{}'".format(type(self), type(other)))
