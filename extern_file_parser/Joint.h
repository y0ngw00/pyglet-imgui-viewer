#ifndef __JOINT_H__
#define __JOINT_H__

#include <string>

#include <Eigen/Core>
#include <Eigen/Geometry>


class Joint
{
public:
    Joint();
    Joint(const std::string& _name, int _parentIndex, const Eigen::MatrixXd& _transform, const std::vector<Eigen::MatrixXd>& _animList);
    
    virtual ~Joint();

    void SetInvBindPose(const Eigen::MatrixXd& _invBindPose) { invBindPose = _invBindPose; }

// Load functions
private:

    void initialize();

public:
    std::string name;
    int parentIndex;
    Eigen::MatrixXd transform;
    Eigen::MatrixXd invBindPose;
    std::vector<Eigen::MatrixXd> animList;
};


#endif
