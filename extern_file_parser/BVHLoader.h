#ifndef __BVH_H__
#define __BVH_H__
#include <string>
#include <vector>
#include <Eigen/Core>
#include <Eigen/Geometry>

class BVH
{
public:
	BVH(const std::string& file);

	void load(const std::string& file);

	const std::vector<std::string>& getHierarchy(){return hierarchy;}
	int getNumFrames(){return mNumFrames;}
	unsigned int GetNumNodes(){return mOffsets.size();}
	unsigned int GetNumJoints(){return mNames.size();}
	const std::vector<std::string>& getNodeNames(){return mNames;}
	const std::vector<Eigen::Vector3d>& getOffsets(){return mOffsets;}
	const std::vector<int>& getParents(){return mParents;}
	double getTimestep(){return mTimestep;}

	const Eigen::Vector3d& getPosition(int idx){return mPositions[idx];}
	const Eigen::MatrixXd& getRotation(int idx){return mRotations[idx];}

	const std::vector<Eigen::Vector3d>& getPositions(){return mPositions;}
	const std::vector<Eigen::MatrixXd>& getRotations(){return mRotations;}

	int getNodeIndex(const std::string& name){auto it = std::find(mNames.begin(), mNames.end(), name); return std::distance(mNames.begin(), it);}

	// Eigen::Isometry3d getReferenceTransform();
	std::vector<Eigen::Isometry3d> forwardKinematics(const Eigen::Vector3d& pos, const Eigen::MatrixXd& rot, int idx);
private:
	std::string mFile;
	std::vector<std::string> mNames;
	std::vector<Eigen::Vector3d> mOffsets;
	std::vector<int> mParents;

	std::vector<std::string> hierarchy;

	int mNumFrames;
	double mTimestep;
	std::vector<Eigen::Vector3d> mPositions; // 1x3
	std::vector<Eigen::MatrixXd> mRotations; // 3*3n

	static Eigen::Matrix3d eulerXYZToMatrix(const Eigen::Vector3d& _angle);
	static Eigen::Matrix3d eulerZXYToMatrix(const Eigen::Vector3d& _angle);
	static Eigen::Matrix3d eulerZYXToMatrix(const Eigen::Vector3d& _angle);
};
#endif