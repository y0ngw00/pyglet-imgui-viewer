import numpy as np
import pyglet
from pyglet import window, app, shapes
from pyglet.math import Mat4, Vec3, Vec4
import math
from pyglet.gl import *
from ctypes import byref

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import Animation
import shader

class CustomGroup(pyglet.graphics.Group):
    '''
    To draw multiple 3D shapes in Pyglet, you should make a group for an object.
    '''
    def __init__(self, object, order):
        """
        Initializes a Primitive object.

        Args:
            object: The object associated with the primitive.
            order: The order in which the primitive should be rendered.
        """
        super().__init__(order)
        self.shader_program = shader.create_program(
            shader.vertex_source_default, shader.fragment_source_default
        )
        self.object = object
        self.indexed_vertices_list = None
        self.shader_program.use()

    def set_state(self):
        self.shader_program.use()
        self.shader_program['model'] = Mat4(self.object.transform_gbl.flatten())

        if self.object.texture is not None:

            self.shader_program['useTexture'] = GL_TRUE
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, self.object.texture.id)

        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, 0)


    def unset_state(self):
        self.shader_program.stop()

    def __eq__(self, other):
        return (self.__class__ is other.__class__ and
                self.order == other.order and
                self.parent == other.parent)
    
    def __hash__(self):
        return hash((self.order))

class Mesh:
    '''
    default structure of mesh
    '''
    def __init__(self):
    
        self.vertices = []
        self.normals = []
        self.uvs = []
        self.colors = ()

        self.indices = []

        self.num_vertices = 0
        self.stride = 3

class CustomMesh(Mesh):
    '''
    structure of custom mesh from external files.
    '''
    def __init__(self, mesh_info):
        super().__init__()
        self.vertices = mesh_info["vertices"]
        self.normals = mesh_info["normals"]
        self.uvs = mesh_info["uvs"]
        
        self.num_vertices = len(self.vertices)//self.stride
        self.colors =(255, 255,255, 255) * self.num_vertices
        self.indices = mesh_info["indices"]
        
        self.skin_weight = []
        self.joint_indices = []
        if "joint_indices" in mesh_info:
            self.joint_indices = mesh_info["joint_indices"]
        if "skin_weight" in mesh_info:
            self.skin_weight = mesh_info["skin_weight"]

    def animate(self, frame):
        if len(self.skin_weight) == 0:
            return

class Cylinder(Mesh):
    '''
    default structure of cylinder
    '''
    def __init__(self,mesh_info):
        super().__init__()
        diameter = mesh_info["diameter"]
        height = mesh_info["height"]
        num_segments = mesh_info["num_segments"]

        radius = diameter / 2.0
        half_height = height / 2.0
        angle_step = 2 * math.pi / num_segments
        
        self.vertices = []
        self.normals = []
        self.uvs = []
        self.indices = []

        # Create top and bottom center points
        self.vertices.extend([0.0, half_height, 0.0, 0.0, -half_height, 0.0])
        self.normals.extend([0.0, 1.0, 0.0, 0.0, -1.0, 0.0])
        self.uvs.extend([0.5, 0.5, 0.5, 0.5])
        
        for i in range(num_segments + 1):
            angle = i * angle_step
            x = radius * math.cos(angle)
            z = radius * math.sin(angle)
            
            # Top circle
            self.vertices.extend([x, half_height, z])
            self.normals.extend([0.0, 1.0, 0.0])
            self.uvs.extend([(x / diameter) + 0.5, (z / diameter) + 0.5])
            
            # Bottom circle
            self.vertices.extend([x, -half_height, z])
            self.normals.extend([0.0, -1.0, 0.0])
            self.uvs.extend([(x / diameter) + 0.5, (z / diameter) + 0.5])
            
            # Side vertices
            self.vertices.extend([x, half_height, z])
            self.normals.extend([x, 0.0, z])
            self.uvs.extend([i / num_segments, 1.0])
            
            self.vertices.extend([x, -half_height, z])
            self.normals.extend([x, 0.0, z])
            self.uvs.extend([i / num_segments, 0.0])

        self.num_vertices = len(self.vertices)//self.stride
        self.colors =(255, 255,255, 255) * self.num_vertices
            
        # Indices for the top and bottom circles
        for i in range(num_segments):
            top_center = 0
            bottom_center = 1
            top_start = 2 + i * 4
            bottom_start = top_start + 1
            top_next = 2 + (i + 1) * 4
            bottom_next = top_next + 1
            
            self.indices.extend([top_center, top_next, top_start])
            self.indices.extend([bottom_center, bottom_start, bottom_next])
            
        # Indices for the sides
        for i in range(num_segments):
            side_top1 = 3 + i * 4
            side_bottom1 = side_top1 + 1
            side_top2 = 3 + (i+1) * 4
            side_bottom2 = side_top2 + 1
            
            self.indices.extend([side_top1, side_top2, side_bottom2])
            self.indices.extend([side_top1, side_bottom2, side_bottom1])
        
class Cube(Mesh):
    '''
    default structure of cube
    '''
    def __init__(self, mesh_info):
        super().__init__()
        self.vertices = [-0.5,-0.5,0.5,
                 0.5,-0.5,0.5,
                 0.5,0.5,0.5,
                 -0.5,0.5,0.5,

                 -0.5,-0.5,-0.5,
                 0.5,-0.5,-0.5,
                 0.5,0.5,-0.5,
                 -0.5,0.5,-0.5,

                 0.5,-0.5,-0.5,
                 0.5,0.5,-0.5,
                 0.5,0.5,0.5,
                 0.5,-0.5,0.5,

                 -0.5,0.5,-0.5,
                 -0.5,-0.5,-0.5,
                 -0.5,-0.5,0.5,
                 -0.5,0.5,0.5,

                 -0.5,-0.5,-0.5,
                 0.5,-0.5,-0.5,
                 0.5,-0.5,0.5,
                 -0.5,-0.5,0.5,

                 0.5,0.5,-0.5,
                 -0.5,0.5,-0.5,
                 -0.5,0.5,0.5,
                 0.5,0.5,0.5
                ]
        
        scale = mesh_info["scale"]
        self.vertices = [scale[idx%3] * x for idx, x in enumerate(self.vertices)]
        self.num_vertices = len(self.vertices)//self.stride

        self.normals = [0.0,0.0,1.0,
                        0.0,0.0,1.0,
                        0.0,0.0,1.0,
                        0.0,0.0,1.0,
                        
                        0.0,0.0,-1.0,
                        0.0,0.0,-1.0,
                        0.0,0.0,-1.0,
                        0.0,0.0,-1.0,
                        
                        1.0,0.0,0.0,
                        1.0,0.0,0.0,
                        1.0,0.0,0.0,
                        1.0,0.0,0.0,
                        
                        -1.0,0.0,0.0,
                        -1.0,0.0,0.0,
                        -1.0,0.0,0.0,
                        -1.0,0.0,0.0,
                        
                        0.0,-1.0,0.0,
                        0.0,-1.0,0.0,
                        0.0,-1.0,0.0,
                        0.0,-1.0,0.0,
                        
                        0.0,1.0,0.0,
                        0.0,1.0,0.0,
                        0.0,1.0,0.0,
                        0.0,1.0,0.0,
                        ]

        for i in range(self.num_vertices):
            self.colors +=(255, 255,255, 255)

        self.uvs = [0.0,0.0,
                    1.0,0.0,
                    1.0,1.0,
                    0.0,1.0,
                    
                    0.0,0.0,
                    1.0,0.0,
                    1.0,1.0,
                    0.0,1.0,
                    
                    0.0,0.0,
                    1.0,0.0,
                    1.0,1.0,
                    0.0,1.0,
                    
                    0.0,0.0,
                    1.0,0.0,
                    1.0,1.0,
                    0.0,1.0,
                    
                    0.0,0.0,
                    1.0,0.0,
                    1.0,1.0,
                    0.0,1.0,
                    
                    0.0,0.0,
                    1.0,0.0,
                    1.0,1.0,
                    0.0,1.0]

        self.indices = [0, 1, 2, 2, 3, 0,
               4, 6, 5, 7, 6, 4,
               8, 9, 10, 10, 11, 8,
               12, 13, 14, 14, 15, 12,
               16, 17, 18, 18, 19, 16,
               20, 21, 22, 22, 23, 20]
        
class GridPlane(Mesh):
    '''
    default structure of plane
    '''
    def __init__(self,mesh_info):
        super().__init__()
        num_x = mesh_info["grid_x"]
        num_z = mesh_info["grid_z"]
        scale = mesh_info["scale"]
        num_face = num_x*num_z
        
        for i in range(num_x):
            xl = - num_x//2 + float(i) - 0.5 
            xr = - num_x//2 + float(i) + 0.5
            for j in range(num_z):
                zl = -num_z//2 + float(j) + 0.5
                zr = -num_z//2 + float(j) - 0.5
                self.vertices += [xl,0.0,zl]
                self.vertices += [xr,0.0,zl]
                self.vertices += [xr,0.0,zr]

                self.vertices += [xl,0.0,zl]
                self.vertices += [xr,0.0,zr]
                self.vertices += [xl,0.0,zr]

                self.normals += [0.0,1.0,0.0]
                self.normals += [0.0,1.0,0.0]
                self.normals += [0.0,1.0,0.0]
                self.normals += [0.0,1.0,0.0]
                self.normals += [0.0,1.0,0.0]
                self.normals += [0.0,1.0,0.0]
                
                self.uvs += [0.0,0.0]
                self.uvs += [1.0,0.0]
                self.uvs += [1.0,1.0]
                self.uvs += [0.0,0.0]
                self.uvs += [1.0,1.0]
                self.uvs += [0.0,1.0]

                if ((i+j)%2==0):
                    self.colors +=(191, 191,191, 255) *6
                else:
                    self.colors +=(134, 125,140, 255) *6

        self.vertices = [scale * x for idx, x in enumerate(self.vertices)]
        self.num_vertices = len(self.vertices)//self.stride
        self.indices = [i for i in range(self.num_vertices)]    

class Sphere(Mesh):
    '''
    default structure of sphere
    '''
    def __init__(self, mesh_info):
        super().__init__()
        stacks = mesh_info["stack"]
        slices = mesh_info["slice"]
        scale= mesh_info["scale"]
        
        num_triangles = 2 * slices * (stacks - 1)

        for i in range(stacks):
            phi0 = 0.5 * math.pi - (i * math.pi) / stacks
            phi1 = 0.5 * math.pi - ((i + 1) * math.pi) / stacks
            coord_v0 = 1.0 - float(i) / stacks
            coord_v1 = 1.0 - float(i + 1) / stacks

            y0 = scale * math.sin(phi0)
            r0 = scale * math.cos(phi0)
            y1 = scale * math.sin(phi1)
            r1 = scale * math.cos(phi1)
            y2 = y1
            y3 = y0

            for j in range(slices):
                theta0 = (j * 2 * math.pi) / slices
                theta1 = ((j + 1) * 2 * math.pi) / slices
                coord_u0 = float(j) / slices
                coord_u1 = float(j + 1) / slices

                x0 = r0 * math.cos(theta0)
                z0 = r0 * math.sin(-theta0)
                u0 = coord_u0
                v0 = coord_v0
                x1 = r1 * math.cos(theta0)
                z1 = r1 * math.sin(-theta0)
                u1 = coord_u0
                v1 = coord_v1
                x2 = r1 * math.cos(theta1)
                z2 = r1 * math.sin(-theta1)
                u2 = coord_u1
                v2 = coord_v1
                x3 = r0 * math.cos(theta1)
                z3 = r0 * math.sin(-theta1)
                u3 = coord_u1
                v3 = coord_v0

                if (i != stacks - 1):
                    self.vertices.append(x0)
                    self.vertices.append(y0)
                    self.vertices.append(z0)
                    self.normals.append(x0)
                    self.normals.append(y0)
                    self.normals.append(z0)
                    self.uvs.append(u0)
                    self.uvs.append(v0)

                    self.vertices.append(x1)
                    self.vertices.append(y1)
                    self.vertices.append(z1)
                    self.normals.append(x1)
                    self.normals.append(y1)
                    self.normals.append(z1)
                    self.uvs.append(u1)
                    self.uvs.append(v1)

                    self.vertices.append(x2)
                    self.vertices.append(y2)
                    self.vertices.append(z2)
                    self.normals.append(x2)
                    self.normals.append(y2)
                    self.normals.append(z2)
                    self.uvs.append(u2)
                    self.uvs.append(v2)

                if (i != 0):
                    self.vertices.append(x2)
                    self.vertices.append(y2)
                    self.vertices.append(z2)
                    self.normals.append(x2)
                    self.normals.append(y2)
                    self.normals.append(z2)
                    self.uvs.append(u2)
                    self.uvs.append(v2)

                    self.vertices.append(x3)
                    self.vertices.append(y3)
                    self.vertices.append(z3)
                    self.normals.append(x3)
                    self.normals.append(y3)
                    self.normals.append(z3)
                    self.uvs.append(u3)
                    self.uvs.append(v3)

                    self.vertices.append(x0)
                    self.vertices.append(y0)
                    self.vertices.append(z0)
                    self.normals.append(x0)
                    self.normals.append(y0)
                    self.normals.append(z0)
                    self.uvs.append(u0)
                    self.uvs.append(v0)
                    
        self.num_vertices = len(self.vertices)//self.stride

        for i in range(self.num_vertices):
            self.colors +=(255, 255,255, 255)

        for i in range(num_triangles*3):
            self.indices.append(i)
