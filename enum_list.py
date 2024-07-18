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
