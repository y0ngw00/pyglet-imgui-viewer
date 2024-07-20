#ifndef __MESH_H__
#define __MESH_H__

#include <string>

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
	std::vector<int> ctrlPoint;
	std::vector<IndexWeightPair> weightPairs;
};


class Mesh
{
public:
    Mesh();
    Mesh(const Eigen::VectorXd& _vertices, const Eigen::VectorXd& _normals, const Eigen::VectorXd& _texCoords, const std::vector<unsigned int>& _indices, const int _stride);
    void SetSkinningData(const std::unordered_map<int, ControlPointInfo>& _skinData);
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
    std::unordered_map<int, ControlPointInfo> mSkinData;
    int mStride;
};


#endif
