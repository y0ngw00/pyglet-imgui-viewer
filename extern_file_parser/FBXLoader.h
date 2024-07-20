#ifndef __FBXLOADER_H__
#define __FBXLOADER_H__

#include "fbxsdk.h"
#include <string>
#include <vector>
#include <Eigen/Core>
#include <Eigen/Geometry>

class Mesh;
class Joint;
class IndexWeightPair;
class ControlPointInfo;
class FBXLoader
{
public:
    FBXLoader();
    bool LoadFBXfromAssimp(const std::string& _filePath);
    bool LoadFBX(const std::string& _filePath);
    void ProcessNode(FbxScene* _scene, FbxNode* node);
    void CreateScene();

    int GetMeshCount();
    int GetMeshStride(int index);
    Eigen::VectorXd GetMeshPosition(int index);
    Eigen::VectorXd GetMeshNormal(int index);
    Eigen::VectorXd GetMeshTextureCoord(int index);
    std::vector<unsigned int> GetMeshPositionIndex(int index);

    const std::string GetJointName(int index);
    int GetJointCount();
    int GetParentIndex(int index);
    const Eigen::MatrixXd GetJointTransform(int index);
    const std::vector<Eigen::MatrixXd> GetJointAnimList(int index);
    
    virtual ~FBXLoader();

// Load functions
private:

    void initialize();
    bool loadScene(FbxManager* _pManager, FbxScene* _scene, const std::string& _pFileName);
    bool loadMesh(FbxNode* _pNode);
    bool loadJoint(FbxScene* _scene, FbxNode* _node);
    void loadSkin(FbxNode* _pNode, std::unordered_map<int, ControlPointInfo>& out_controlPointsInfo);
    int FindJointIndexByName(const std::string& _jointName);
    void DebugSumOfWeights(std::unordered_map<int, ControlPointInfo>& out_controlPointsInfo);


// Utility functions
private:
    void GetPolygons(FbxMesh* _pMesh);
    FbxAMatrix GetGeometry(FbxNode* _pNode);
    FbxAMatrix GetNodeTransform(FbxNode* _pNode);
    FbxAMatrix EigenToFbxMatrix(const Eigen::MatrixXd& _mat, float _scale=1.0f);
    Eigen::MatrixXd FbxToEigenMatrix(const FbxAMatrix& _mat, float _scale=1.0f);
    Eigen::Quaterniond FbxToEigenQuaternion(const FbxAMatrix& _fbxMatrix);

private:
    std::vector<Mesh*> m_Meshes;
    std::vector<Joint*> m_Joints;
};

#endif

