#ifndef __FBXLOADER_H__
#define __FBXLOADER_H__

#include "fbxsdk.h"
#include <string>
#include <vector>
#include <Eigen/Core>
#include <Eigen/Geometry>

class Mesh;
class Joint;
class FBXLoader
{
public:
    FBXLoader();
    void ClearSDK();
    bool LoadFBX(const std::string& _filePath);
    void ProcessNode(FbxNode* node);
    void CreateScene();

    int GetMeshCount();
    int GetMeshStride(int index);
    Eigen::VectorXd GetMeshPosition(int index);
    Eigen::VectorXd GetMeshNormal(int index);
    Eigen::VectorXd GetMeshTextureCoord(int index);
    Eigen::VectorXi GetMeshPositionIndex(int index);

    std::string GetJointName(int index);
    int GetJointCount();
    int GetParentIndex(int index);
    Eigen::MatrixXd GetJointTransform(int index);
    
    virtual ~FBXLoader();

// Load functions
private:

    void initialize();
    bool loadScene(FbxManager* _pManager, const std::string& _pFileName);
    bool loadMesh(FbxNode* _pNode);
    bool loadJoint(FbxNode* _node);

// Utility functions
private:
    void GetPolygons(FbxMesh* _pMesh);
    FbxAMatrix GetGeometry(FbxNode* _pNode);
    FbxAMatrix GetNodeTransform(FbxNode* _pNode);
    FbxAMatrix EigenToFbxMatrix(const Eigen::MatrixXd& _mat, float _scale=1.0f);
    Eigen::MatrixXd FbxToEigenMatrix(const FbxAMatrix& _mat, float _scale=1.0f);
    Eigen::Quaterniond FbxToEigenQuaternion(const FbxAMatrix& _fbxMatrix);

private:
    FbxScene* m_fbxScene;

    std::vector<Mesh*> m_Meshes;
    std::vector<Joint*> m_Joints;
};

#endif

