#include "FBXLoader.h"
#include <fstream>
#include <iostream>
#include <vector>
#include <unordered_map>

#include <Eigen/Core>
#include <Eigen/Geometry>

#include <pybind11/pybind11.h>
#include <pybind11/embed.h>
#include <pybind11/numpy.h>
#include <pybind11/eigen.h>
#include <pybind11/stl.h>

#include "Mesh.h"
#include "Joint.h"
using namespace fbxsdk;

struct SubMesh
{
    unsigned int m_IndexOffset;
    unsigned int m_TriangleCount;

    SubMesh()
    {
        m_IndexOffset = 0;
        m_TriangleCount = 0;
    }
};

FBXLoader::
FBXLoader()
{
    initialize();
}

FBXLoader::
~FBXLoader()
{
    m_Joints.clear();
    m_Meshes.clear();
}

void
FBXLoader::
initialize()
{
}

bool
FBXLoader::
LoadFBX(const std::string& _filePath)
{

    FbxManager* sdkManager = FbxManager::Create();

    std::cout<<"Load FBX file from : "<<_filePath<<"\n";

    FbxScene* fbxScene = FbxScene::Create(sdkManager, "");

    // Create a geometry converter
    FbxGeometryConverter converter(sdkManager);

    // Triangulate the scene
    bool result = converter.Triangulate(fbxScene, /*replace=*/true);
    if (!result) {
        std::cerr << "Failed to triangulate the scene" << std::endl;
        return false;
    }
    bool bLoadResult = loadScene(sdkManager, fbxScene, _filePath);
    if(bLoadResult == false)
    {
        std::cout<<"Some errors occurred while loading the scene.."<<"\n";
        std::cout<<"Failed to load FBX file from : "<<_filePath<<"\n";
        return bLoadResult;
    }
    //Check Fbx Nodes normality

    //Scale

    //load mesh
    FbxNode* rootNode = fbxScene->GetRootNode();

    this->ProcessNode(fbxScene, rootNode);

    for(int i=0; i<m_meshNodes.size(); i++)
    {
        loadMesh(m_meshNodes[i]);
    }

    bool bLoadTexture = loadTexture(fbxScene);

    // FbxAMatrix globalPosition = globalPosition = rootNode->EvaluateGlobalTransform();
    // if(rootNode->GetNodeAttribute()) 
	// {
	// // 	//geometry offset 값은 자식 노드에 상속되지 않는다.
	// 	FbxAMatrix geometryOffset = GetGeometry(rootNode);
	// 	FbxAMatrix globalOffPosition = globalPosition * geometryOffset;

	// }

    //Delete the FBX Manager. All the objects that have been allocated using the FBX Manager and that haven't been explicitly destroyed are also automatically destroyed.
    if (fbxScene)
	{
		fbxScene->Destroy();
		fbxScene = NULL;
	}

    if( sdkManager ) sdkManager->Destroy();
	if( bLoadResult ) FBXSDK_printf("Program Success!\n");

    return true;

}

void FBXLoader::ProcessNode(FbxScene* _scene, FbxNode* node) {
    // Process the node's attributes.
    for(int i = 0; i < node->GetNodeAttributeCount(); i++) {
        FbxNodeAttribute* attribute = node->GetNodeAttributeByIndex(i);

        switch(attribute->GetAttributeType()) {
        case FbxNodeAttribute::eMesh:
            if(node!=nullptr) 
                m_meshNodes.push_back(node);

            break;
        case FbxNodeAttribute::eSkeleton:
        {
            if(node!=nullptr)
                loadJoint(_scene, node);
            break;
        }
            
        default:
            break;
        }
    }

    // Recursively process the node's children.
    for(int j = 0; j < node->GetChildCount(); j++) {
        ProcessNode(_scene, node->GetChild(j));
    }
}


bool
FBXLoader::
loadMesh(FbxNode* _pNode)
{
    FbxMesh* lMesh = (FbxMesh*) _pNode->GetNodeAttribute ();
    if(lMesh == nullptr)
    {
        std::cout<<"Mesh Node attribute is not valid"<<"\n";
        return false;
    }

    FbxAMatrix globalPosition = globalPosition = _pNode->EvaluateGlobalTransform();
    if(_pNode->GetNodeAttribute()) 
	{
	// 	//geometry offset 값은 자식 노드에 상속되지 않는다.
		FbxAMatrix geometryOffset = GetGeometry(_pNode);
		FbxAMatrix globalOffPosition = globalPosition * geometryOffset;

	}

    int numVertices = lMesh->GetControlPointsCount();
    int numPolygons = lMesh->GetPolygonCount();
    FbxVector4* controlPoints = lMesh->GetControlPoints();
    // Process the vertices.

    Eigen::VectorXd pos(numVertices*3);
    Eigen::VectorXd nor(numVertices*3);
    Eigen::VectorXd uvs(numVertices*2);
    std::vector<unsigned int> indices;
    std::vector<unsigned int> uv_indices;

    // Process the normals.
    FbxGeometryElementNormal* normalElement = lMesh->GetElementNormal();
    FbxGeometryElementUV* uvElement = lMesh->GetElementUV();

    bool bProcessNormal = normalElement != nullptr;
    bool bProcessUV = uvElement != nullptr;;

    for(int i = 0; i < numVertices; i++) 
    {
        FbxVector4 position = controlPoints[i];
        pos[i*3] = position[0];
        pos[i*3+1] = position[1];
        pos[i*3+2] = position[2];
        if(bProcessNormal) 
        {
            FbxVector4 normal = normalElement->GetDirectArray().GetAt(i);
            nor[i*3] = normal[0];
            nor[i*3+1] = normal[1];
            nor[i*3+2] = normal[2];
        }

        // Process the UVs.
        if(bProcessUV)
        {
            FbxVector2 uv = uvElement->GetDirectArray().GetAt(i);
            uvs[i*2] = uv[0];
            uvs[i*2+1] = uv[1];
        }

    }

    bool bUseIndex = uvElement->GetReferenceMode() != FbxGeometryElement::eDirect;
    unsigned int polyIndexCounter = 0;
    for(int i = 0; i < numPolygons; i++) 
    {
        int polygonSize = lMesh->GetPolygonSize(i);
        std::vector<unsigned int> polygonindex;
        std::vector<unsigned int> textureindex;

        for(int j = 0; j < polygonSize; j++) 
        {
            int vertexIndex = lMesh->GetPolygonVertex(i, j);
            polygonindex.push_back(vertexIndex);


            if(bProcessUV)
            {
                unsigned int uvIndex = bUseIndex? uvElement->GetIndexArray().GetAt(polyIndexCounter) : polyIndexCounter;
                if (uvIndex < 0)
                    uvIndex = 0;
                
                polyIndexCounter++;
                textureindex.push_back(uvIndex);
            }
        }
        
        // force to triangulate quad meshes (limitation of the current implementation)
        if (lMesh->GetPolygonSize(i) == 4)
        {
            unsigned int index_four = polygonindex[3];
            unsigned int index_two = polygonindex[1];
            polygonindex.insert(polygonindex.begin()+2, index_two);
            polygonindex.insert(polygonindex.begin()+2, index_four);

            unsigned int uv_index_four = textureindex[3];
            unsigned int uv_index_two = textureindex[1];
            textureindex.insert(textureindex.begin()+2, uv_index_two);
            textureindex.insert(textureindex.begin()+2, uv_index_four);
        }
        indices.insert( indices.end(), polygonindex.begin(), polygonindex.end() );
        uv_indices.insert( uv_indices.end(), textureindex.begin(), textureindex.end() );
    }

    for (int i = 0; i < indices.size(); i++)
    {
        unsigned int positionIndex = indices[i];
        int uvIndex = uv_indices[i];

        FbxVector2 uvValue = uvElement->GetDirectArray().GetAt(uvIndex);
        uvs[2 * positionIndex] = uvValue[0];
        uvs[2 * positionIndex + 1] = uvValue[1];
    }

    Mesh* mesh = new Mesh(pos, nor, uvs, indices, 3);

    std::vector<ControlPointInfo>  out_controlPointsInfo;
    out_controlPointsInfo.resize(numVertices);
    loadSkin(_pNode,out_controlPointsInfo);

    mesh->SetSkinningData(out_controlPointsInfo);

    m_Meshes.push_back(mesh);

    return true;

}

bool
FBXLoader::
loadJoint(FbxScene* _scene, FbxNode* _node)
{
    if(_node == nullptr)
    {
        std::cout<<"Skeleton is not valid"<<"\n";
        return false;
    }
	FbxSkeleton* curSkel = _node->GetSkeleton();
	if(curSkel)
	{
		///local matrix로 변환
        std::string name = _node->GetName();
        int parentIndex = -1;
        FbxNode* parent = _node->GetParent();
        if(parent)
        {
            std::string parentName = parent->GetName();
            for(int i=0; i<m_Joints.size(); i++)
            {
                if(m_Joints[i]->GetName() == parentName)
                {
                    parentIndex = i;
                    break;
                }
            }
        }
        FbxAMatrix geometryOffset = GetGeometry(_node);
		FbxAMatrix localMatrix = _node->EvaluateLocalTransform();

		Eigen::MatrixXd m= FbxToEigenMatrix(localMatrix, 1.0f);

        //Get Animation information
        std::vector<Eigen::MatrixXd> animList;
        FbxAnimStack *currAnimStack = _scene->GetSrcObject<FbxAnimStack>(0);
        if (currAnimStack != nullptr)
        {
            FbxString animStackName = currAnimStack->GetName();
            FbxTakeInfo *takeInfo = _scene->GetTakeInfo(animStackName);
            FbxTime start = currAnimStack->GetLocalTimeSpan().GetStart();
            FbxTime end = currAnimStack->GetLocalTimeSpan().GetStop();

            for (FbxLongLong i = start.GetFrameCount(FbxTime::eFrames30); i != end.GetFrameCount(FbxTime::eFrames30); ++i) {
                FbxTime currTime;
                currTime.SetFrame(i, FbxTime::eFrames30);
                FbxAMatrix currTransform = _node->EvaluateLocalTransform(currTime);
                Eigen::MatrixXd m= FbxToEigenMatrix(currTransform, 1.0f);
                animList.push_back(m);
            }
        }

        // std::cout<<"Joint "<<m_Joints.size()<<": "<<name<<"\n";

        m_Joints.push_back(new Joint(name, parentIndex, m, animList));
	}
    return true;
}

void
FBXLoader::
loadSkin(FbxNode* _pNode, std::vector<ControlPointInfo>& out_controlPointsInfo)
{
    FbxMesh* mesh = (FbxMesh*) _pNode->GetNodeAttribute ();
    if(mesh == nullptr)
    {
        std::cout<<"Mesh Node attribute is not valid"<<"\n";
        return;
    }
    unsigned int numOfDeformers = mesh->GetDeformerCount();

	//Get transform matrix
	FbxAMatrix geometryTransform = _pNode->EvaluateGlobalTransform();
	//A deformer is a FBX thing, which contains some clusters
	//A cluster contains a link, which is basically a joint
	//Normally, there is only one deformer in a mesh
    // std::cout<<mesh->GetName()<<"'s deformer count : "<<numOfDeformers<<"\n";
	for (unsigned int deformerIndex = 0; deformerIndex != numOfDeformers; ++deformerIndex) {
		//There are many types of deformers in FBX
		//We are using only skins, so we see if there is a skin
		FbxSkin *currSkin = reinterpret_cast<FbxSkin*>(mesh->GetDeformer(deformerIndex, FbxDeformer::eSkin));
		if (!currSkin) {
			continue;
		}

		unsigned int numOfClusters = currSkin->GetClusterCount();
        // std::cout<<mesh->GetName()<<"'s cluster count : "<<numOfClusters<<"\n";

		for (unsigned int clusterIndex = 0; clusterIndex != numOfClusters; ++clusterIndex) {
			FbxCluster *currCluster = currSkin->GetCluster(clusterIndex);
            if(currCluster)
            {
                FbxString currJointName = currCluster->GetLink()->GetName();
                int currJointIndex = FindJointIndexByName(std::string(currJointName.Buffer()));
                if (currJointIndex == -1) {
                    FBXSDK_printf("error: can't find the joint: %s\n\n", currJointName);
                    continue;
                }

                //FbxAMatrix transformMatrix;
                FbxAMatrix transformLinkMatrix;
                //FbxAMatrix globalBindPoseInverseMatrix;
                //
                //currCluster->GetTransformMatrix(transformMatrix);
                currCluster->GetTransformLinkMatrix(transformLinkMatrix);
                FbxAMatrix globalBindPoseInverseMatrix = transformLinkMatrix.Inverse();
                //globalBindPoseInverseMatrix = transformLinkMatrix.Inverse() * transformMatrix * geometryTransform;

                m_Joints[currJointIndex]->SetInvBindPose(FbxToEigenMatrix(globalBindPoseInverseMatrix));

                unsigned int numOfIndices = currCluster->GetControlPointIndicesCount();
                // std::cout<<"cluster "<<clusterIndex<<"'s indices and weights count : "<<numOfIndices<<"\n";

                int* indices = currCluster->GetControlPointIndices();
                double* weights = currCluster->GetControlPointWeights();
                for (unsigned int i = 0; i != numOfIndices; ++i) {
                    // IndexWeightPair weightPair;
                    // weightPair.index = clusterIndex;		
                    // weightPair.weight = weights[i];		//weight to control point of current joint
                    //add index-weight pair into ControlPointInfo Struct
                    out_controlPointsInfo[indices[i]].skin_joints.push_back(currJointIndex);
                    out_controlPointsInfo[indices[i]].skin_weights.push_back(weights[i]);
                }
            }
			
		}
	}


    DebugSumOfWeights(out_controlPointsInfo);		//should be 1.0

}

bool
FBXLoader::

loadTexture(FbxScene* _scene)
{
    int lMaterialCount = _scene->GetMaterialCount();
    for (int i = 0; i < lMaterialCount; i++) {
        FbxSurfaceMaterial* lMaterial = _scene->GetMaterial(i);

        // Get the texture count of each type
        int lTextureCount = _scene->GetTextureCount();

        for (int j = 0; j < lTextureCount; j++) {
            // Get the texture
            FbxTexture* lTexture = _scene->GetTexture(j);
            FbxFileTexture * lFileTexture = FbxCast<FbxFileTexture>(lTexture);
            // Now you have the texture, you can get its information
            // Check if the texture is embedded

            if (lFileTexture->GetRelativeFileName()) {
                // Get the texture data
                // const char* lData = static_cast<const char*>(lFileTexture->GetUserDataPtr());
                const FbxString lFileName = lFileTexture->GetFileName();

                const FbxString lAbsFbxFileName = FbxPathUtils::Resolve(lFileName);
                std::cout<<"Texture file name : "<<lAbsFbxFileName<<"\n";
			    const FbxString lAbsFolderName = FbxPathUtils::GetFolderName(lAbsFbxFileName);
                std::cout<<"Texture folder name : "<<lAbsFolderName<<"\n";
                const FbxString lResolvedFileName = FbxPathUtils::Bind(lAbsFolderName, lFileTexture->GetRelativeFileName());
                std::cout<<"Texture resolved file name : "<<lResolvedFileName<<"\n"; 

                for (auto& mesh : m_Meshes) {
                    mesh->SetDiffuseTexture(lFileName.Buffer());
                }
                break;
            }
        }
    }

    return true;
}

int
FBXLoader::
FindJointIndexByName(const std::string& _jointName)
{
    for(int i=0; i<m_Joints.size(); i++)
    {
        if(m_Joints[i]->GetName() == _jointName)
        {
            return i;
        }
    }
    return -1;
}

void
FBXLoader::
DebugSumOfWeights(std::vector<ControlPointInfo>& out_controlPointsInfo)
{
	for (const auto& it : out_controlPointsInfo) {
		std::vector<float> skin_weights = it.skin_weights;
		double sumOfWeights = 0.0;
	//	FBXSDK_printf("\joint id		weight\n");
		for (auto& skin_weight : skin_weights) {
		//	FBXSDK_printf("%d		%lf\n", weightPair.index, weightPair.weight);
			sumOfWeights += skin_weight;
		}
		//FBXSDK_printf("the sum of weights is: %lf\n", sumOfWeights);
		assert((sumOfWeights - 1.0) < 10e-5);	//sum of weight is not equal to 1.0
	}
}

// Check the fbx sdk version and load fbx Scene.
bool
FBXLoader::
loadScene(FbxManager* _pManager, FbxScene* _scene, const std::string& _pFileName)
{
    int sdkMajor,  sdkMinor,  sdkRevision;
    int fileMajor, fileMinor, fileRevision;
    bool bResult = true;

    // create an importer.

    FbxImporter* fbxImporter = nullptr;
    fbxImporter = FbxImporter::Create( _pManager, "" );
    // Initialize the importer by providing a filename.
    bool importStatus = false;
    if (fbxImporter != nullptr) {
       importStatus = fbxImporter->Initialize(_pFileName.c_str(), -1, _pManager->GetIOSettings());
        // Rest of the code...
    } else {
        // Handle the case when fbxImporter is null
        // Print an error message or throw an exception
    }

	if(!importStatus)
	{
		std::cout<<"Failed to initialize FBX Importer" <<"\n";
		std::cout << fbxImporter->GetStatus().GetErrorString();
        return false;
	}
    // Get the file version number generate by the FBX SDK.
	FbxManager::GetFileFormatVersion(sdkMajor, sdkMinor, sdkRevision);

    fbxImporter->GetFileVersion(fileMajor, fileMinor, fileRevision);

    // std::cout<<"FBX SDK version is "<< sdkMajor<<" "<<sdkMinor<<" "<< sdkRevision<<"\n";
    // std::cout<<"FBX file format version SDK is "<< fileMajor<<" "<<fileMinor<<" "<< fileRevision<<"\n";

    ///major, minor, revision 까지 체크 
    unsigned int fileVersion = (fileMajor << 16 | fileMinor << 8 | fileRevision);
    unsigned int sdkVersion = (sdkMajor << 16 | sdkMinor << 8 | sdkRevision);

    if( fileVersion != sdkVersion )
    {			
        std::cout<<"The fbx file version is different from fbx sdk version."<<"\n";
        bResult = true; ///sdk version이 틀려도 loading이 가능할 수 있음.  단 경고창은 보여줘야함.
    }

    if (fbxImporter->IsFBX())
    {
        
        // Set the import states. By default, the import states are always set to 
        // true. The code below shows how to change these states.
        // _pManager->GetIOSettings()->SetBoolProp(IMP_FBX_MATERIAL,        true);
        // _pManager->GetIOSettings()->SetBoolProp(IMP_FBX_TEXTURE,         true);
        // _pManager->GetIOSettings()->SetBoolProp(IMP_FBX_LINK,            true);
        // _pManager->GetIOSettings()->SetBoolProp(IMP_FBX_SHAPE,           true);
        // _pManager->GetIOSettings()->SetBoolProp(IMP_FBX_GOBO,            true);
        // _pManager->GetIOSettings()->SetBoolProp(IMP_FBX_ANIMATION,       true);
        // _pManager->GetIOSettings()->SetBoolProp(IMP_FBX_GLOBAL_SETTINGS, true);
    }

    //Import the scene.
    bResult = fbxImporter->Import(_scene);
    if(bResult==false && fbxImporter->GetStatus() == FbxStatus::ePasswordError)
    {
        std::cout<<"This file requires password."<<"\n";
        return false;
    }

    if(bResult==false || fbxImporter->GetStatus() != FbxStatus::eSuccess)
    {
        if(bResult)
        {
            std::cout<<"The importer was able to read the file but some error occurs."<<'\n';
            std::cout<<"Loaded scene may be incomplete."<<'\n';
        }
        else
        {
            std::cout<<"Importer failed to load the FBX file."<<'\n';
        }

        FbxArray<FbxString*> history;
		fbxImporter->GetStatus().GetErrorStringHistory(history);
		if (history.GetCount() > 1)
		{
			std::cout<<"   Error history stack: "<<"\n";
			for (int i = 0; i < history.GetCount(); i++)
			{
				std::cout<<history[i]->Buffer()<<"\n";
			}
		}
		FbxArrayDelete<FbxString*>(history);
    }

    fbxImporter->Destroy();

	return bResult;
}

FbxAMatrix
FBXLoader::
GetGeometry(FbxNode* _pNode)
{
    const FbxVector4 translation = _pNode->GetGeometricTranslation(FbxNode::eSourcePivot);
    const FbxVector4 rotation = _pNode->GetGeometricRotation(FbxNode::eSourcePivot);
    const FbxVector4 scaling = _pNode->GetGeometricScaling(FbxNode::eSourcePivot);

    return FbxAMatrix(translation, rotation, scaling);
}

int 
FBXLoader::
GetMeshCount()
{
    return m_Meshes.size();
}

int
FBXLoader::
GetMeshStride(int index)
{
    return m_Meshes[index]->GetStride();
}

Eigen::VectorXd
FBXLoader::
GetMeshPosition(int index)
{
    Mesh* mesh = m_Meshes[index];
    return mesh->GetVertices();
}

Eigen::VectorXd
FBXLoader::
GetMeshNormal(int index)
{
    Mesh* mesh = m_Meshes[index];
    return mesh->GetNormals();
}

Eigen::VectorXd
FBXLoader::
GetMeshTextureCoord(int index)
{
    Mesh* mesh = m_Meshes[index];
    return mesh->GetTexCoords();
}

std::vector<unsigned int>
FBXLoader::
GetMeshPositionIndex(int index)
{
    Mesh* mesh = m_Meshes[index];
    return mesh->GetIndices();
}

const
std::vector<unsigned int>
FBXLoader::
GetMeshSkinJoints(int mesh_index, int vertex_index)
{
    Mesh* mesh = m_Meshes[mesh_index];
    return mesh->GetMeshSkinJoints(vertex_index);
}

const
std::vector<float>
FBXLoader::
GetMeshSkinWeights(int mesh_index, int vertex_index)
{
    Mesh* mesh = m_Meshes[mesh_index];
    return mesh->GetMeshSkinWeights(vertex_index);
}

const
std::vector<ControlPointInfo>
FBXLoader::
GetMeshSkinData(int mesh_index)
{
    Mesh* mesh = m_Meshes[mesh_index];
    return mesh->GetSkinningData();
}

const
std::vector<Joint*>
FBXLoader::
GetJoints()
{
    return m_Joints;
}

const
std::vector<Mesh*>
FBXLoader::
GetMeshes()
{
    return m_Meshes;
}
FbxAMatrix
FBXLoader::
GetNodeTransform(FbxNode* _pNode)
{
	FbxAMatrix translationM, scalingM, scalingPivotM, scalingOffsetM, rotationOffsetM, rotationPivotM,
                preRotationM, rotationM, postRotationM, transformM;

	FbxVector4 translation = _pNode->LclTranslation.Get();
    FbxVector4 preRotation = _pNode->PreRotation.Get();
	FbxVector4 postRotation = _pNode->PostRotation.Get();
	FbxVector4 rotation = _pNode->LclRotation.Get();
	FbxVector4 scaling = _pNode->LclScaling.Get();
	FbxVector4 scalingOffset = _pNode->ScalingOffset.Get();
    FbxVector4 scalingPivot = _pNode->ScalingPivot.Get();
    FbxVector4 rotationOffset = _pNode->RotationOffset.Get();
    FbxVector4 rotationPivot = _pNode->RotationPivot.Get();

	translationM.SetIdentity();
	translationM.SetT(translation);

	scalingM.SetIdentity();
	scalingM.SetS(scaling);

	scalingPivotM.SetIdentity();
	scalingPivotM.SetT(scalingPivot);

	scalingOffsetM.SetIdentity();
	scalingOffsetM.SetT(scalingOffset);

	rotationOffsetM.SetIdentity();
	rotationOffsetM.SetT(rotationOffset);

	rotationPivotM.SetIdentity();
	rotationPivotM.SetT(rotationPivot);

	preRotationM.SetIdentity();
	preRotationM.SetR(preRotation);

	rotationM.SetIdentity();
	rotationM.SetR(rotation);

	postRotationM.SetIdentity();
	postRotationM.SetR(postRotation);

	transformM = translationM * rotationOffsetM * rotationPivotM * preRotationM * rotationM * postRotationM * rotationPivotM.Inverse() *
		scalingOffsetM * scalingPivotM * scalingM * scalingPivotM.Inverse();

	return transformM;
}

FbxAMatrix 
FBXLoader::
EigenToFbxMatrix(const Eigen::MatrixXd& _mat, float _scale)
{
    FbxAMatrix fbxMatrix;
	fbxMatrix.mData[0][0] = _mat(0,0);			fbxMatrix.mData[1][0] = _mat(1,0);			fbxMatrix.mData[2][0] = _mat(2,0);			fbxMatrix.mData[3][0] = _mat(3,0) * _scale;
	fbxMatrix.mData[0][1] = _mat(0,1);			fbxMatrix.mData[1][1] = _mat(1,1);			fbxMatrix.mData[2][1] = _mat(2,1);			fbxMatrix.mData[3][1] = _mat(3,1) * _scale;
	fbxMatrix.mData[0][2] = _mat(0,2);			fbxMatrix.mData[1][2] = _mat(1,2);			fbxMatrix.mData[2][2] = _mat(2,2);			fbxMatrix.mData[3][2] = _mat(3,2) * _scale;
	fbxMatrix.mData[0][3] = _mat(0,3);			fbxMatrix.mData[1][3] = _mat(1,3);			fbxMatrix.mData[2][3] = _mat(2,3);			fbxMatrix.mData[3][3] = _mat(3,3);
	return fbxMatrix;
}

#include <Eigen/Dense>

Eigen::MatrixXd
FBXLoader::
FbxToEigenMatrix(const FbxAMatrix& _fbxMatrix, float _scale)
{
    Eigen::MatrixXd mat(4,4);
    mat(0,0) = _fbxMatrix.Get(0, 0); mat(1,0) = _fbxMatrix.Get(1, 0); mat(2,0) = _fbxMatrix.Get(2, 0); mat(3,0) = _fbxMatrix.Get(3, 0) * _scale;
    mat(0,1) = _fbxMatrix.Get(0, 1); mat(1,1) = _fbxMatrix.Get(1, 1); mat(2,1) = _fbxMatrix.Get(2, 1); mat(3,1) = _fbxMatrix.Get(3, 1) * _scale;
    mat(0,2) = _fbxMatrix.Get(0, 2); mat(1,2) = _fbxMatrix.Get(1, 2); mat(2,2) = _fbxMatrix.Get(2, 2); mat(3,2) = _fbxMatrix.Get(3, 2) * _scale;
    mat(0,3) = _fbxMatrix.Get(0, 3); mat(1,3) = _fbxMatrix.Get(1, 3); mat(2,3) = _fbxMatrix.Get(2, 3); mat(3,3) = _fbxMatrix.Get(3, 3);
    return mat;
}

Eigen::Quaterniond
FBXLoader::
FbxToEigenQuaternion(const FbxAMatrix& _fbxMatrix)
{
    FbxQuaternion fbxQuat = _fbxMatrix.GetQ();
    return Eigen::Quaterniond(fbxQuat.GetAt(0),fbxQuat.GetAt(1),fbxQuat.GetAt(2),fbxQuat.GetAt(3));
}

namespace py = pybind11;

PYBIND11_MODULE(pycomcon, m){
    py::class_<ControlPointInfo>(m, "ControlPointInfo")
        .def(py::init<>())
        .def_readwrite("skin_weights", &ControlPointInfo::skin_weights)
        .def_readwrite("skin_joints", &ControlPointInfo::skin_joints);
    py::class_<Joint>(m, "Joint")
        .def(py::init<>())
        .def_readwrite("name", &Joint::name)
        .def_readwrite("transform", &Joint::transform)
        .def_readwrite("invBindPose", &Joint::invBindPose)
        .def_readwrite("parentIndex", &Joint::parentIndex)
        .def_readwrite("animList", &Joint::animList);
    py::class_<Mesh>(m, "Mesh")
        .def(py::init<>())
        .def_readwrite("vertices", &Mesh::mVertices)
        .def_readwrite("normals", &Mesh::mNormals)
        .def_readwrite("texCoords", &Mesh::mTexCoords)
        .def_readwrite("indices", &Mesh::mIndices)
        .def_readwrite("diffuseTexture", &Mesh::mDiffuseTexture)
        .def_readwrite("skinData", &Mesh::mSkinData)
        .def_readwrite("stride", &Mesh::mStride);
	py::class_<FBXLoader>(m, "FBXLoader")
		.def(py::init<>())
        .def("load_fbx", &FBXLoader::LoadFBX)
        .def("get_mesh_count", &FBXLoader::GetMeshCount)
        .def("get_mesh_stride", &FBXLoader::GetMeshStride)
        .def("get_mesh_position", &FBXLoader::GetMeshPosition)
        .def("get_mesh_normal", &FBXLoader::GetMeshNormal)
        .def("get_mesh_texcoord", &FBXLoader::GetMeshTextureCoord)
        .def("get_mesh_indices", &FBXLoader::GetMeshPositionIndex)
        .def("get_mesh_skin_data", &FBXLoader::GetMeshSkinData)
        .def("get_mesh_skin_joints", &FBXLoader::GetMeshSkinJoints)
        .def("get_mesh_skin_weights", &FBXLoader::GetMeshSkinWeights)
        .def("get_joints", &FBXLoader::GetJoints)
        .def("get_meshes", &FBXLoader::GetMeshes);
}