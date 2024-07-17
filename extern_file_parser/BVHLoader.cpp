#include "BVHLoader.h"
#include <fstream>
#include <iostream>
#include <sstream>
#include <iterator>
#include <algorithm>
#include <regex>

BVH::
BVH(const std::string& file)
	:mFile(file)
{
	this->load(mFile);
}

void
BVH::
load(const std::string& file)
{

	std::string str;

	std::ifstream ifsh(mFile);
	if(!(ifsh.is_open()))
	{
		std::cout<<"Can't read file "<<file<<std::endl;
		exit(0);
	}
	while(!ifsh.eof())
	{
		
		str.clear();
		std::getline(ifsh,str);
		if(str.size() == 0)
			continue;
		if(str.find("MOTION") != std::string::npos)
			break;
		hierarchy.push_back(str);
	}
	ifsh.close();

	std::ifstream ifs(file);

	std::regex root_expr("\\s*ROOT\\s(\\w+)\\s*");
	std::regex offset_expr("\\s*OFFSET\\s+([\\-\\d\\.e]+)\\s+([\\-\\d\\.e]+)\\s+([\\-\\d\\.e]+)\\s*");
	std::regex channel6_expr("\\s*CHANNELS\\s+6\\s+(\\S+)\\s+(\\S+)\\s+(\\S+)\\s+(\\S+)\\s+(\\S+)\\s+(\\S+)\\s*");
	std::regex channel3_expr("\\s*CHANNELS\\s+3\\s+(\\S+)\\s+(\\S+)\\s+(\\S+)\\s*");
	std::regex joint_expr("\\s*JOINT\\s+(\\w+)\\s*");
	std::regex frame_expr("\\s*Frames\\s*:\\s*([\\-\\d\\.e]+)\\s*");
	std::regex frame_time_expr("\\s*Frame Time\\s*:\\s*([\\-\\d\\.e]+)\\s*");
	std::smatch what;

	

	bool end_site = false;
	int active = -1;
	std::vector<std::string> channel_order;

	while(!ifs.eof())
	{
		
		str.clear();
		std::getline(ifs,str);
		if(str.size() == 0)
			continue;
		if(str.find("HIERARCHY") != std::string::npos)
			continue;
		if(str.find("MOTION") != std::string::npos)
			continue;
		if(std::regex_match(str,what,root_expr))
		{
			mNames.emplace_back(what[1]);
			mOffsets.emplace_back(Eigen::Vector3d::Zero());
			mParents.emplace_back(active);
			active = mParents.size() - 1;
			continue;
		}
		if(str.find("{") != std::string::npos)
			continue;
		if(str.find("}") != std::string::npos){
			if(end_site) end_site = false;
			else active = mParents[active];
			continue;
		}
		
		if(std::regex_match(str,what,offset_expr))
		{
			if(end_site == false){
				Eigen::Vector3d offset = Eigen::Vector3d(std::stod(what[1]),std::stod(what[2]),std::stod(what[3]));
				mOffsets[active] = 0.01*offset;
			}
			continue;
		}
		if(std::regex_match(str,what,channel6_expr))
		{
			for(int i =0;i<6;i++)
				channel_order.emplace_back(what[i+1]);
			continue;
		}
		if(std::regex_match(str,what,channel3_expr))
		{
			for(int i =0;i<3;i++)
				channel_order.emplace_back(what[i+1]);
			continue;
		}

		if(std::regex_match(str,what,joint_expr))
		{
			mNames.emplace_back(what[1]);
			mOffsets.emplace_back(Eigen::Vector3d::Zero());
			mParents.emplace_back(active);
			active = mParents.size() - 1;
			continue;
		}

		if(str.find("End Site") != std::string::npos){
			end_site = true;
			continue;
		}

		if(std::regex_match(str,what,frame_expr)){
			mNumFrames = std::stoi(what[1]);
			mPositions.reserve(mNumFrames);
			mRotations.reserve(mNumFrames);
			continue;
		}

		if(std::regex_match(str,what,frame_time_expr)){
			mTimestep = std::stod(what[1]);
			continue;
		}

		std::stringstream ss;
		ss.str(str);
		double val;
		Eigen::VectorXd m_t(channel_order.size());

		for(int i =0;i<channel_order.size();i++)
			ss>>m_t[i];
		mPositions.emplace_back(m_t.head<3>()*0.01);
		int n = m_t.rows()/3-1;
		mRotations.emplace_back(Eigen::MatrixXd::Zero(3,3*n));
		int col = 0;
		for(int i=3;i<m_t.rows();i+=3)
		{
			std::vector<int> order;
			for(int j=0;j<3;j++)
			{
				if(channel_order[i+j] == "Xposition" || channel_order[i+j] == "XPOSITION")
					order.emplace_back(0);
				else if(channel_order[i+j] == "Yposition" || channel_order[i+j] == "YPOSITION")
					order.emplace_back(1);
				else if(channel_order[i+j] == "Zposition" || channel_order[i+j] == "ZPOSITION")
					order.emplace_back(2);
				else if(channel_order[i+j] == "Xrotation" || channel_order[i+j] == "XROTATION")
					order.emplace_back(3);
				else if(channel_order[i+j] == "Yrotation" || channel_order[i+j] == "YROTATION")
					order.emplace_back(4);
				else if(channel_order[i+j] == "Zrotation" || channel_order[i+j] == "ZROTATION")
					order.emplace_back(5);
			}
			if(order[0] == 0) //Position
				continue;
			else if(order[0] == 3 && order[1] == 4 && order[2] == 5)
				mRotations.back().block<3,3>(0,col*3) = eulerXYZToMatrix(m_t.segment<3>(i)*M_PI/180.0);
			else if(order[0] == 5 && order[1] == 3 && order[2] == 4)
				mRotations.back().block<3,3>(0,col*3) = eulerZXYToMatrix(m_t.segment<3>(i)*M_PI/180.0);
			else if(order[0] == 5 && order[1] == 4 && order[2] == 3)
				mRotations.back().block<3,3>(0,col*3) = eulerZYXToMatrix(m_t.segment<3>(i)*M_PI/180.0);
			else
			{
				std::cout<<"Not supported order"<<std::endl;
				exit(0);
			}
			col++;
			
		}
	}
	ifs.close();
}

std::vector<Eigen::Isometry3d>
BVH::
forwardKinematics(const Eigen::Vector3d& position, const Eigen::MatrixXd& rotation, int idx)
{
	std::vector<Eigen::Isometry3d> Ts;


	int current = idx;
	int count = 0;
	while(current != -1)
	{
		if(mParents[current] == -1){
			Eigen::Isometry3d T;
			T.linear() = rotation.block<3,3>(0,3*current);
			T.translation() = position;
			Ts.emplace_back(T);
		}
		else
		{
			Eigen::Isometry3d T;
			T.linear() = rotation.block<3,3>(0,3*current);
			T.translation() = mOffsets[current];
			Ts.emplace_back(T);
		}
		count++;
		current = mParents[current];
	}
	for(int i=count-2;i>=0;i--)
		Ts[i] = Ts[i+1]*Ts[i];

	return Ts;
}
Eigen::Matrix3d
BVH::
eulerXYZToMatrix(const Eigen::Vector3d& _angle) {
  // +-           -+   +-                                        -+
  // | r00 r01 r02 |   |  cy*cz           -cy*sz            sy    |
  // | r10 r11 r12 | = |  cz*sx*sy+cx*sz   cx*cz-sx*sy*sz  -cy*sx |
  // | r20 r21 r22 |   | -cx*cz*sy+sx*sz   cz*sx+cx*sy*sz   cx*cy |
  // +-           -+   +-                                        -+

  Eigen::Matrix3d ret;

  double cx = cos(_angle[0]);
  double sx = sin(_angle[0]);
  double cy = cos(_angle[1]);
  double sy = sin(_angle[1]);
  double cz = cos(_angle[2]);
  double sz = sin(_angle[2]);

  ret(0, 0) = cy*cz;
  ret(1, 0) = cx*sz + cz*sx*sy;
  ret(2, 0) = sx*sz - cx*cz*sy;

  ret(0, 1) = -cy*sz;
  ret(1, 1) =  cx*cz - sx*sy*sz;
  ret(2, 1) =  cz*sx + cx*sy*sz;

  ret(0, 2) =  sy;
  ret(1, 2) = -cy*sx;
  ret(2, 2) =  cx*cy;

  return ret;
}
Eigen::Matrix3d
BVH::
eulerZXYToMatrix(const Eigen::Vector3d& _angle) {
  // +-           -+   +-                                        -+
  // | r00 r01 r02 |   |  cy*cz-sx*sy*sz  -cx*sz   cz*sy+cy*sx*sz |
  // | r10 r11 r12 | = |  cz*sx*sy+cy*sz   cx*cz  -cy*cz*sx+sy*sz |
  // | r20 r21 r22 |   | -cx*sy            sx      cx*cy          |
  // +-           -+   +-                                        -+

  Eigen::Matrix3d ret;

  double cz = cos(_angle(0));
  double sz = sin(_angle(0));
  double cx = cos(_angle(1));
  double sx = sin(_angle(1));
  double cy = cos(_angle(2));
  double sy = sin(_angle(2));

  ret(0, 0) =  cy*cz-sx*sy*sz;
  ret(1, 0) =  cz*sx*sy+cy*sz;
  ret(2, 0) = -cx*sy;

  ret(0, 1) = -cx*sz;
  ret(1, 1) =  cx*cz;
  ret(2, 1) =  sx;

  ret(0, 2) =  cz*sy+cy*sx*sz;
  ret(1, 2) = -cy*cz*sx+sy*sz;
  ret(2, 2) =  cx*cy;

  return ret;
}
Eigen::Matrix3d
BVH::
eulerZYXToMatrix(const Eigen::Vector3d& _angle) {
  // +-           -+   +-                                      -+
  // | r00 r01 r02 |   |  cy*cz  cz*sx*sy-cx*sz  cx*cz*sy+sx*sz |
  // | r10 r11 r12 | = |  cy*sz  cx*cz+sx*sy*sz -cz*sx+cx*sy*sz |
  // | r20 r21 r22 |   | -sy     cy*sx           cx*cy          |
  // +-           -+   +-                                      -+

  Eigen::Matrix3d ret;

  double cz = cos(_angle[0]);
  double sz = sin(_angle[0]);
  double cy = cos(_angle[1]);
  double sy = sin(_angle[1]);
  double cx = cos(_angle[2]);
  double sx = sin(_angle[2]);

  ret(0, 0) =  cz*cy;
  ret(1, 0) =  sz*cy;
  ret(2, 0) = -sy;

  ret(0, 1) = cz*sy*sx - sz*cx;
  ret(1, 1) = sz*sy*sx + cz*cx;
  ret(2, 1) = cy*sx;

  ret(0, 2) = cz*sy*cx + sz*sx;
  ret(1, 2) = sz*sy*cx - cz*sx;
  ret(2, 2) = cy*cx;

  return ret;
}
