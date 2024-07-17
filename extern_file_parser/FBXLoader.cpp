#include "FBXLoader.h"
#include <fstream>
#include <iostream>
#include <vector>

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

FBXLoader::
FBXLoader()
{
    initialize();
}

FBXLoader::
~FBXLoader()
{
    clearSDK();

    m_Joints.clear();
    m_Meshes.clear();
}

void
FBXLoader::
initialize()
{
    m_fbxScene = NULL;
}

void
FBXLoader::
clearSDK()
{	
	if (m_fbxScene)
	{
		m_fbxScene->Destroy();
		m_fbxScene = NULL;
	}


}

bool
FBXLoader::
LoadFBX(const std::string& _filePath)
{

    FbxManager* sdkManager = FbxManager::Create();

    std::cout<<"Load FBX file from : "<<_filePath<<"\n";

    m_fbxScene = FbxScene::Create(sdkManager, "");
    bool bLoadResult = loadScene(sdkManager, _filePath);
    if(bLoadResult == false)
    {
        std::cout<<"Some errors occurred while loading the scene.."<<"\n";
        std::cout<<"Failed to load FBX file from : "<<_filePath<<"\n";
        return bLoadResult;
    }
    //Check Fbx Nodes normality

    //Scale

    //load mesh
    FbxNode* rootNode = m_fbxScene->GetRootNode();

    this->ProcessNode(rootNode);
    FbxAMatrix globalPosition = globalPosition = rootNode->EvaluateGlobalTransform();
    if(rootNode->GetNodeAttribute()) 
	{
	// 	//geometry offset 값은 자식 노드에 상속되지 않는다.
		FbxAMatrix geometryOffset = GetGeometry(rootNode);
		FbxAMatrix globalOffPosition = globalPosition * geometryOffset;

	}


    //load texture 

    //load joint

    //load skinning


    // // Display the scene.
    // DisplayMetaData(m_fbxScene);

    // FBXSDK_printf("\n\n---------------------\nGlobal Light Settings\n---------------------\n\n");

    // if( gVerbose ) DisplayGlobalLightSettings(&m_fbxScene->GetGlobalSettings());

    // FBXSDK_printf("\n\n----------------------\nGlobal Camera Settings\n----------------------\n\n");

    // if( gVerbose ) DisplayGlobalCameraSettings(&m_fbxScene->GetGlobalSettings());

    // FBXSDK_printf("\n\n--------------------\nGlobal Time Settings\n--------------------\n\n");

    // if( gVerbose ) DisplayGlobalTimeSettings(&m_fbxScene->GetGlobalSettings());

    // FBXSDK_printf("\n\n---------\nHierarchy\n---------\n\n");

    // if( gVerbose ) DisplayHierarchy(&m_fbxScenene);

    // FBXSDK_printf("\n\n------------\nNode Content\n------------\n\n");

    // if( gVerbose ) DisplayContent(m_fbxScene);

    // FBXSDK_printf("\n\n----\nPose\n----\n\n");

    // if( gVerbose ) DisplayPose(m_fbxScene);

    // FBXSDK_printf("\n\n---------\nAnimation\n---------\n\n");

    // if( gVerbose ) DisplayAnimation(m_fbxScene);

    // //now display generic information

    // FBXSDK_printf("\n\n---------\nGeneric Information\n---------\n\n");
    // if( gVerbose ) DisplayGenericInfo(m_fbxScene);

    //Delete the FBX Manager. All the objects that have been allocated using the FBX Manager and that haven't been explicitly destroyed are also automatically destroyed.
    if( sdkManager ) sdkManager->Destroy();
	if( bLoadResult ) FBXSDK_printf("Program Success!\n");

    return true;

}

void FBXLoader::ProcessNode(FbxNode* node) {
    // Process the node's attributes.
    for(int i = 0; i < node->GetNodeAttributeCount(); i++) {
        FbxNodeAttribute* attribute = node->GetNodeAttributeByIndex(i);

        switch(attribute->GetAttributeType()) {
        case FbxNodeAttribute::eMesh:
            // if(node!=nullptr) m_meshNodes.push_back(node);
            loadMesh(node);
            break;
        case FbxNodeAttribute::eSkeleton:
        {
            if(node!=nullptr)
                loadJoint(node);
            break;
        }
            
        default:
            break;
        }
    }

    // Recursively process the node's children.
    for(int j = 0; j < node->GetChildCount(); j++) {
        ProcessNode(node->GetChild(j));
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
    int numPolygonVertices = lMesh->GetPolygonSize(0);
    FbxVector4* controlPoints = lMesh->GetControlPoints();
    std::cout<<"Number of vertices : "<<numVertices<<"\n";
    // Process the vertices.

    Eigen::VectorXd pos(numVertices*3);
    Eigen::VectorXd nor(numVertices*3);
    Eigen::VectorXd uvs(numVertices*2);
    Eigen::VectorXi indices(numPolygons*numPolygonVertices);

    // Process the normals.
    FbxGeometryElementNormal* normalElement = lMesh->GetElementNormal();
    FbxGeometryElementUV* uvElement = lMesh->GetElementUV();

    bool bProcessNormal = normalElement != nullptr && normalElement->GetMappingMode() == FbxGeometryElement::eByControlPoint;
    bool bProcessUV = uvElement != nullptr && uvElement->GetMappingMode() == FbxGeometryElement::eByControlPoint;

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

    // Process the vertex indices.

    for(int i = 0; i < numPolygons; i++) {
        for(int j = 0; j < numPolygonVertices; j++) {
            int vertexIndex = lMesh->GetPolygonVertex(i, j);
            indices[i*numPolygonVertices+j] = vertexIndex;
            // Now vertexIndex is the index of a vertex of the polygon.
        }
    }

    Mesh* mesh = new Mesh(pos, nor, uvs, indices);

    m_Meshes.push_back(mesh);

    return true;

}

bool
FBXLoader::
loadJoint(FbxNode* _node)
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
		FbxAMatrix localMatrix = GetNodeTransform(_node);

		Eigen::MatrixXd m= FbxToEigenMatrix(localMatrix, 1.0f);
        
        m_Joints.push_back(new Joint(name, parentIndex, m));
		// m_JointList.push_back(_node);
	}
    return true;
	//return tf;
}

// Check the fbx sdk version and load fbx Scene.
bool
FBXLoader::
loadScene(FbxManager* _pManager, const std::string& _pFileName)
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

    std::cout<<"FBX SDK version is "<< sdkMajor<<" "<<sdkMinor<<" "<< sdkRevision<<"\n";
    std::cout<<"FBX file format version SDK is "<< fileMajor<<" "<<fileMinor<<" "<< fileRevision<<"\n";

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
    bResult = fbxImporter->Import(m_fbxScene);
    std::cout<<"FBX SDK versi"<<"\n";
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

void
FBXLoader::
GetPolygons(FbxMesh* _pMesh)
{
    int lPolygonCount = _pMesh->GetPolygonCount();
    FbxVector4* lControlPoints = _pMesh->GetControlPoints(); 
    char header[100];

    int vertexId = 0;
    for (int i = 0; i < lPolygonCount; i++)
    {
        for (int l = 0; l < _pMesh->GetElementPolygonGroupCount(); l++)
        {
            FbxGeometryElementPolygonGroup* lePolgrp = _pMesh->GetElementPolygonGroup(l);
			switch (lePolgrp->GetMappingMode())
			{
			case FbxGeometryElement::eByPolygon:
				if (lePolgrp->GetReferenceMode() == FbxGeometryElement::eIndex)
				{
					int polyGroupId = lePolgrp->GetIndexArray().GetAt(i);
					break;
				}
			default:
				// any other mapping modes don't make sense
				std::cout<<("        \"unsupported group assignment\"")<<"\n";
				break;
			}
        }

        int lPolygonSize = _pMesh->GetPolygonSize(i);

	// 	for (int j = 0; j < lPolygonSize; j++)
	// 	{
	// 		int lControlPointIndex = _pMesh->GetPolygonVertex(i, j);
	// 		if (lControlPointIndex < 0)
	// 		{
	// 			std::cout<<"         Coordinates: Invalid index found!"<<"\n";
	// 			continue;
	// 		}

	// 		for (int l = 0; l < _pMesh->GetElementVertexColorCount(); l++)
	// 		{
	// 			FbxGeometryElementVertexColor* leVtxc = _pMesh->GetElementVertexColor( l);
	// 			FBXSDK_sprintf(header, 100, "            Color vertex: "); 

	// 			switch (leVtxc->GetMappingMode())
	// 			{
	// 			default:
	// 			    break;
	// 			case FbxGeometryElement::eByControlPoint:
	// 				switch (leVtxc->GetReferenceMode())
	// 				{
	// 				case FbxGeometryElement::eDirect:
	// 					DisplayColor(header, leVtxc->GetDirectArray().GetAt(lControlPointIndex));
	// 					break;
	// 				case FbxGeometryElement::eIndexToDirect:
	// 					{
	// 						int id = leVtxc->GetIndexArray().GetAt(lControlPointIndex);
	// 						DisplayColor(header, leVtxc->GetDirectArray().GetAt(id));
	// 					}
	// 					break;
	// 				default:
	// 					break; // other reference modes not shown here!
	// 				}
	// 				break;

	// 			case FbxGeometryElement::eByPolygonVertex:
	// 				{
	// 					switch (leVtxc->GetReferenceMode())
	// 					{
	// 					case FbxGeometryElement::eDirect:
	// 						DisplayColor(header, leVtxc->GetDirectArray().GetAt(vertexId));
	// 						break;
	// 					case FbxGeometryElement::eIndexToDirect:
	// 						{
	// 							int id = leVtxc->GetIndexArray().GetAt(vertexId);
	// 							DisplayColor(header, leVtxc->GetDirectArray().GetAt(id));
	// 						}
	// 						break;
	// 					default:
	// 						break; // other reference modes not shown here!
	// 					}
	// 				}
	// 				break;

	// 			case FbxGeometryElement::eByPolygon: // doesn't make much sense for UVs
	// 			case FbxGeometryElement::eAllSame:   // doesn't make much sense for UVs
	// 			case FbxGeometryElement::eNone:       // doesn't make much sense for UVs
	// 				break;
	// 			}
	// 		}
	// 		for (int l = 0; l < _pMesh->GetElementUVCount(); ++l)
	// 		{
	// 			FbxGeometryElementUV* leUV = _pMesh->GetElementUV( l);
	// 			FBXSDK_sprintf(header, 100, "            Texture UV: "); 

	// 			switch (leUV->GetMappingMode())
	// 			{
	// 			default:
	// 			    break;
	// 			case FbxGeometryElement::eByControlPoint:
	// 				switch (leUV->GetReferenceMode())
	// 				{
	// 				case FbxGeometryElement::eDirect:
	// 					Display2DVector(header, leUV->GetDirectArray().GetAt(lControlPointIndex));
	// 					break;
	// 				case FbxGeometryElement::eIndexToDirect:
	// 					{
	// 						int id = leUV->GetIndexArray().GetAt(lControlPointIndex);
	// 						Display2DVector(header, leUV->GetDirectArray().GetAt(id));
	// 					}
	// 					break;
	// 				default:
	// 					break; // other reference modes not shown here!
	// 				}
	// 				break;

	// 			case FbxGeometryElement::eByPolygonVertex:
	// 				{
	// 					int lTextureUVIndex = _pMesh->GetTextureUVIndex(i, j);
	// 					switch (leUV->GetReferenceMode())
	// 					{
	// 					case FbxGeometryElement::eDirect:
	// 					case FbxGeometryElement::eIndexToDirect:
	// 						{
	// 							Display2DVector(header, leUV->GetDirectArray().GetAt(lTextureUVIndex));
	// 						}
	// 						break;
	// 					default:
	// 						break; // other reference modes not shown here!
	// 					}
	// 				}
	// 				break;

	// 			case FbxGeometryElement::eByPolygon: // doesn't make much sense for UVs
	// 			case FbxGeometryElement::eAllSame:   // doesn't make much sense for UVs
	// 			case FbxGeometryElement::eNone:       // doesn't make much sense for UVs
	// 				break;
	// 			}
	// 		}
	// 		for(int l = 0; l < _pMesh->GetElementNormalCount(); ++l)
	// 		{
	// 			FbxGeometryElementNormal* leNormal = _pMesh->GetElementNormal( l);
	// 			FBXSDK_sprintf(header, 100, "            Normal: "); 

	// 			if(leNormal->GetMappingMode() == FbxGeometryElement::eByPolygonVertex)
	// 			{
	// 				switch (leNormal->GetReferenceMode())
	// 				{
	// 				case FbxGeometryElement::eDirect:
	// 					Display3DVector(header, leNormal->GetDirectArray().GetAt(vertexId));
	// 					break;
	// 				case FbxGeometryElement::eIndexToDirect:
	// 					{
	// 						int id = leNormal->GetIndexArray().GetAt(vertexId);
	// 						Display3DVector(header, leNormal->GetDirectArray().GetAt(id));
	// 					}
	// 					break;
	// 				default:
	// 					break; // other reference modes not shown here!
	// 				}
	// 			}

	// 		}
	// 		for(int l  = 0; l < _pMesh->GetElementTangentCount(); ++l)
	// 		{
	// 			FbxGeometryElementTangent* leTangent = _pMesh->GetElementTangent( l);
	// 			FBXSDK_sprintf(header, 100, "            Tangent: "); 

	// 			if(leTangent->GetMappingMode() == FbxGeometryElement::eByPolygonVertex)
	// 			{
	// 				switch (leTangent->GetReferenceMode())
	// 				{
	// 				case FbxGeometryElement::eDirect:
	// 					Display3DVector(header, leTangent->GetDirectArray().GetAt(vertexId));
	// 					break;
	// 				case FbxGeometryElement::eIndexToDirect:
	// 					{
	// 						int id = leTangent->GetIndexArray().GetAt(vertexId);
	// 						Display3DVector(header, leTangent->GetDirectArray().GetAt(id));
	// 					}
	// 					break;
	// 				default:
	// 					break; // other reference modes not shown here!
	// 				}
	// 			}

	// 		}
	// 		for(int l = 0; l < _pMesh->GetElementBinormalCount(); ++l)
	// 		{

	// 			FbxGeometryElementBinormal* leBinormal = _pMesh->GetElementBinormal( l);

	// 			FBXSDK_sprintf(header, 100, "            Binormal: "); 
	// 			if(leBinormal->GetMappingMode() == FbxGeometryElement::eByPolygonVertex)
	// 			{
	// 				switch (leBinormal->GetReferenceMode())
	// 				{
	// 				case FbxGeometryElement::eDirect:
	// 					Display3DVector(header, leBinormal->GetDirectArray().GetAt(vertexId));
	// 					break;
	// 				case FbxGeometryElement::eIndexToDirect:
	// 					{
	// 						int id = leBinormal->GetIndexArray().GetAt(vertexId);
	// 						Display3DVector(header, leBinormal->GetDirectArray().GetAt(id));
	// 					}
	// 					break;
	// 				default:
	// 					break; // other reference modes not shown here!
	// 				}
	// 			}
	// 		}
			vertexId++;
		// } // for polygonSize
    } // for polygonCount
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

Eigen::VectorXi
FBXLoader::
GetMeshPositionIndex(int index)
{
    Mesh* mesh = m_Meshes[index];
    return mesh->GetIndices();
}

std::string
FBXLoader::
GetJointName(int index)
{
    return m_Joints[index]->GetName();
}

int
FBXLoader::
GetJointCount()
{
    return m_Joints.size();
}


int
FBXLoader::
GetParentIndex(int index)
{
    return m_Joints[index]->GetParentIndex();
}


Eigen::MatrixXd
FBXLoader::
GetJointTransform(int index)
{
    return m_Joints[index]->GetTransform();
    // Joint* node = m_Joints[index];
    // const FbxVector4 translation = node->GetGeometricTranslation(FbxNode::eSourcePivot);
    // const FbxVector4 rotation = node->GetGeometricRotation(FbxNode::eSourcePivot);
    // const FbxVector4 scaling = node->GetGeometricScaling(FbxNode::eSourcePivot);

    // FbxMatrix fbxM =  FbxAMatrix(translation, rotation, scaling);
    // FbxAMatrix fbxM = GetNodeTransform(node);
    // return FbxToEigenMatrix(fbxM);
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
	py::class_<FBXLoader>(m, "FBXLoader")
		.def(py::init<>())
        .def("load_fbx", &FBXLoader::LoadFBX)
        .def("get_mesh_count", &FBXLoader::GetMeshCount)
        .def("get_mesh_position", &FBXLoader::GetMeshPosition)
        .def("get_mesh_normal", &FBXLoader::GetMeshNormal)
        .def("get_mesh_texcoord", &FBXLoader::GetMeshTextureCoord)
        .def("get_mesh_indices", &FBXLoader::GetMeshPositionIndex)
        .def("get_joint_name", &FBXLoader::GetJointName)
        .def("get_joint_count", &FBXLoader::GetJointCount)
        .def("get_parent_idx", &FBXLoader::GetParentIndex)
        .def("get_joint_transform", &FBXLoader::GetJointTransform);
}