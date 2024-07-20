#ifndef __MESH_H__
#define __MESH_H__

#include <string>

#include <Eigen/Core>
#include <Eigen/Geometry>


class Mesh
{
public:
    Mesh();
    Mesh(const Eigen::VectorXd& _vertices, const Eigen::VectorXd& _normals, const Eigen::VectorXd& _texCoords, const Eigen::VectorXi& _indices, const int _stride);
    
    virtual ~Mesh();

    Eigen::VectorXd GetVertices() const { return mVertices; }
    Eigen::VectorXd GetNormals() const { return mNormals; }
    Eigen::VectorXd GetTexCoords() const { return mTexCoords; }
    std::vector<unsigned int> GetIndices() const { return mIndices; }
    int GetStride() const { return mStride; }

// Load functions
private:

    void initialize();

private:
    Eigen::VectorXd mVertices;
    Eigen::VectorXd mNormals;
    Eigen::VectorXd mTexCoords;
    std::vector<unsigned int> mIndices;
    int mStride;
};


#endif
