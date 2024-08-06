#ifndef __MESH_H__
#define __MESH_H__

#include <string>
#include <vector>
#include <Eigen/Core>
#include <Eigen/Geometry>
#include <unordered_map>

struct IndexWeightPair
{
	unsigned int index;	//index of joint 
	double weight;		//weight of influence by the joint
	IndexWeightPair() :
		index(0), weight(0.0)
	{}
};

struct ControlPointInfo
{
	std::vector<unsigned int> skin_joints;
	std::vector<float> skin_weights;
};


class Mesh
{
public:
    Mesh();
    Mesh(const Eigen::VectorXd& _vertices, const Eigen::VectorXd& _normals, const Eigen::VectorXd& _texCoords, const std::vector<unsigned int>& _indices, const int _stride);
    void SetSkinningData(const std::vector<ControlPointInfo> & _skinData);
    void SetDiffuseTexture(const std::string& _diffuseTexture);
    virtual ~Mesh();

    Eigen::VectorXd GetVertices() const { return mVertices; }
    Eigen::VectorXd GetNormals() const { return mNormals; }
    Eigen::VectorXd GetTexCoords() const { return mTexCoords; }
    std::vector<unsigned int> GetIndices() const { return mIndices; }
    int GetStride() const { return mStride; }

    const std::vector<unsigned int> GetMeshSkinJoints(int vertex_index);
    const std::vector<float> GetMeshSkinWeights(int vertex_index);
    const std::vector<ControlPointInfo>& GetSkinningData() const { return mSkinData; }

// Load functions
private:

    void initialize();

public:
    Eigen::VectorXd mVertices;
    Eigen::VectorXd mNormals;
    Eigen::VectorXd mTexCoords;
    std::vector<unsigned int> mIndices;
    std::vector<ControlPointInfo> mSkinData;
    std::string mDiffuseTexture;
    int mStride;
};


#endif
