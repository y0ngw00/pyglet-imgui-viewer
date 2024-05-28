import math
import numpy as np
import pyglet
from pyglet.math import Mat4, Vec3, Vec4

EPS = 1e-6

def normalize(x):
    x_normed = x / (np.linalg.norm(x) + 1e-6)
    return x_normed

def glet_multiply(m,v):
    if len(v) ==4:
        result = Vec4(0)
        for i in range(4):
            result[i] = (m[i*4] * v[0] +
                        m[i*4 + 1] * v[1] +
                        m[i*4 + 2] * v[2] +
                        m[i*4 + 3] * v[3])
    elif len(v)==3:
        stride = 4 if len(m)==16 else 3
        result = Vec3(0)
        for i in range(3):
            result[i] = (m[i*stride] * v[0] +
                        m[i*stride + 1] * v[1] +
                        m[i*stride + 2] * v[2])
    return result

def get_trackball_point(r, dx, dy):
    dxdx_dydy = dx*dx + dy*dy
    if r*r > dxdx_dydy:
        return np.array([dx/r, dy/r, (r*r - dxdx_dydy)**0.5 / r])
    else:
        return np.array([dx/r, dy/r, 0.0])
    

def angleaxis_to_quat(angle,axis):
    q = [0,0,0,0]
    q[0] = np.cos(angle/2)
    q[1] = axis[0] * np.sin(angle/2)
    q[2] = axis[1] * np.sin(angle/2)
    q[3] = axis[2] * np.sin(angle/2)

    return q

def quat_to_mat(quat):
    """
    Convert a quaternion to a rotation matrix.

    :param q: Quaternion in the form [w, x, y, z].
    :return: Rotation matrix.
    """
    w, x, y, z = quat
    Nq = w*w + x*x + y*y + z*z
    if Nq > 0.0:
        s = 2.0 / Nq
    else:
        s = 0.0
    X = x * s
    Y = y * s
    Z = z * s
    wX = w * X
    wY = w * Y
    wZ = w * Z
    xX = x * X
    xY = x * Y
    xZ = x * Z
    yY = y * Y
    yZ = y * Z
    zZ = z * Z
    return np.array([1.0 - (yY + zZ), xY - wZ, xZ + wY, 0.0,
                     xY + wZ, 1.0 - (xX + zZ), yZ - wX, 0.0,
                     xZ - wY, yZ + wX, 1.0 - (xX + yY), 0.0,
                     0.0, 0.0, 0.0, 1.0])

def compute_normal(vertices, indices):
    # Initialize normal array
    normals = np.zeros((len(vertices)), dtype=np.float32)

    if len(indices) == 0:
        # Calculate normals using consecutive vertices
        for i in range(0, len(vertices)//(3 * 3)):
            v0 = np.array(vertices[3*i : 3*i +3], dtype=np.float32)
            v1 = np.array(vertices[3*i+3 : 3*i +6], dtype=np.float32)
            v2 = np.array(vertices[3*i+6 : 3*i +9], dtype=np.float32)

            # Compute the normal of the triangle
            edge1 = v1 - v0
            edge2 = v2 - v0
            triangle_normal = np.cross(edge1, edge2)
            triangle_normal /= np.linalg.norm(triangle_normal)

            # Accumulate the normals for each vertex
            normals[3*i : 3*i +3] = triangle_normal
            normals[3*i+3 : 3*i +6] = triangle_normal
            normals[3*i+6 : 3*i +9] = triangle_normal

    else:
        # Calculate normals
        for i in range(0, len(indices), 3):
            i0 = indices[i]
            i1 = indices[i+1]
            i2 = indices[i+2]
            v0 = np.array(vertices[3*i0 : 3*i0+3], dtype=np.float32)
            v1 = np.array(vertices[3*i1 : 3*i1+3], dtype=np.float32)
            v2 = np.array(vertices[3*i2 : 3*i2+3], dtype=np.float32)

            # Compute the normal of the triangle
            edge1 = v1 - v0
            edge2 = v2 - v0
            triangle_normal = np.cross(edge1, edge2)
            triangle_normal /= np.linalg.norm(triangle_normal)

            # Accumulate the normals for each vertex
            normals[3*i0 : 3*i0+3] += triangle_normal
            normals[3*i0 : 3*i1+3] += triangle_normal
            normals[3*i0 : 3*i2+3] += triangle_normal

        # Normalize the accumulated normals
        normals = normals.reshape(len(vertices)//3, 3)
        normals /= np.linalg.norm(normals, axis=1)[:, np.newaxis]
        normals = normals.reshape(-1)

    return normals.tolist()
