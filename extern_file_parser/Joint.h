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

    std::string GetName() const { return name; }
    int GetParentIndex() const { return parentIndex; }
    Eigen::MatrixXd GetTransform() const { return transform; }
    std::vector<Eigen::MatrixXd> GetAnimList() const { return animList; }

// Load functions
private:

    void initialize();

private:
    std::string name;
    int parentIndex;
    Eigen::MatrixXd transform;
    std::vector<Eigen::MatrixXd> animList;
};


#endif
