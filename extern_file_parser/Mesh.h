#ifndef __MESH_H__
#define __MESH_H__

#include <string>

#include <Eigen/Core>
#include <Eigen/Geometry>


class Mesh
{
public:
    Mesh();
    Mesh(const Eigen::VectorXd& _vertices, const Eigen::VectorXd& _normals, const Eigen::VectorXd& _texCoords, const Eigen::VectorXi& _indices);
    
    virtual ~Mesh();

    Eigen::VectorXd GetVertices() const { return mVertices; }
    Eigen::VectorXd GetNormals() const { return mNormals; }
    Eigen::VectorXd GetTexCoords() const { return mTexCoords; }
    Eigen::VectorXi GetIndices() const { return mIndices; }

// Load functions
private:

    void initialize();

private:
    Eigen::VectorXd mVertices;
    Eigen::VectorXd mNormals;
    Eigen::VectorXd mTexCoords;
    Eigen::VectorXi mIndices;
};


#endif
