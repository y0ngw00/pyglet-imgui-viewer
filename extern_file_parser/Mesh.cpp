#include "Mesh.h"
#include <vector>
#include <iostream>
#include <Eigen/Core>
#include <Eigen/Geometry>

Mesh::
Mesh()
{
}

Mesh::
Mesh(const Eigen::VectorXd& _vertices, const Eigen::VectorXd& _normals, const Eigen::VectorXd& _texCoords, const std::vector<unsigned int>& _indices, const int _stride)
{
    mVertices = _vertices;
    mNormals = _normals;
    mTexCoords = _texCoords;
    mIndices = _indices;
    mStride = _stride;
}

const 
std::vector<unsigned int>
Mesh::
GetMeshSkinJoints(int vertex_index)
{
    return mSkinData[vertex_index].skin_joints;
}

const std::vector<float>
Mesh::
GetMeshSkinWeights(int vertex_index)
{
    return mSkinData[vertex_index].skin_weights;
}

void 
Mesh::
SetSkinningData(const std::vector<ControlPointInfo> & _skinData)
{
    mSkinData = _skinData;
}

Mesh::
~Mesh()
{
}


