#include "Mesh.h"
#include <vector>

#include <Eigen/Core>
#include <Eigen/Geometry>

Mesh::
Mesh()
{
}

Mesh::
Mesh(const Eigen::VectorXd& _vertices, const Eigen::VectorXd& _normals, const Eigen::VectorXd& _texCoords, const Eigen::VectorXi& _indices, const int _stride)
{
    mVertices = _vertices;
    mNormals = _normals;
    mTexCoords = _texCoords;
    mIndices = _indices;
    mStride = _stride;
}

Mesh::
~Mesh()
{
}


