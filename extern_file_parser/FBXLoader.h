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
    bool LoadFBX(const std::string& _filePath);
    void ProcessNode(FbxScene* _scene, FbxNode* node);
    void CreateScene();

    int GetMeshCount();
    int GetMeshStride(int index);
    Eigen::VectorXd GetMeshPosition(int index);
    Eigen::VectorXd GetMeshNormal(int index);
    Eigen::VectorXd GetMeshTextureCoord(int index);
    std::vector<unsigned int> GetMeshPositionIndex(int index);
    
    const std::vector<unsigned int> GetMeshSkinJoints(int mesh_index, int vertex_index);
    const std::vector<float> GetMeshSkinWeights(int mesh_index, int vertex_index);
    const std::vector<ControlPointInfo> GetMeshSkinData(int mesh_index);

    const std::vector<Joint*> GetJoints();
    const std::vector<Mesh*> GetMeshes();
    
    virtual ~FBXLoader();

// Load functions
private:

    void initialize();
    bool loadScene(FbxManager* _pManager, FbxScene* _scene, const std::string& _pFileName);
    bool loadMesh(FbxNode* _pNode);
    bool loadJoint(FbxScene* _scene, FbxNode* _node);
    void loadSkin(FbxNode* _pNode, std::vector<ControlPointInfo>& out_controlPointsInfo);
    bool loadTexture(FbxScene* _scene);
    int FindJointIndexByName(const std::string& _jointName);
    void DebugSumOfWeights(std::vector<ControlPointInfo>& out_controlPointsInfo);


// Utility functions
private:
    void GetPolygons(FbxMesh* _pMesh);
    FbxAMatrix GetGeometry(FbxNode* _pNode);
    FbxAMatrix GetNodeTransform(FbxNode* _pNode);
    FbxAMatrix EigenToFbxMatrix(const Eigen::MatrixXd& _mat, float _scale=1.0f);
    Eigen::MatrixXd FbxToEigenMatrix(const FbxAMatrix& _mat, float _scale=1.0f);
    Eigen::Quaterniond FbxToEigenQuaternion(const FbxAMatrix& _fbxMatrix);

private:
    std::vector<FbxNode*> m_meshNodes;
    std::vector<Mesh*> m_Meshes;
    std::vector<Joint*> m_Joints;
};

#endif

