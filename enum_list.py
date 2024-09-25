from enum import Enum

class MeshType(Enum):
    Custom = 0
    Sphere = 1
    Cube = 2
    GridPlane = 3
    Cylinder = 4


class FileType(Enum):
    Character=0
    Audio=1
    Network=2
    Motion=3

class Boundary(Enum):
    Right = 0
    Left = 1
    Up = 2
    Down = 3
    
class MotionPart(Enum):
    FULL = 0
    UPPER = 1
    LOWER = 2
    
class FormationMode(Enum):
    NORMAL = 0
    DRAW = 1
    
class SamplingType(Enum):
    BOUNDARY = 0,
    UNIFORM = 1,
    GRID = 2,
    
class LayoutMode(Enum):
    FULL = 0
    HALF = 1