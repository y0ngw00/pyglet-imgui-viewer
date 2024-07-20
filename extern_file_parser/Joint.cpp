#include "Joint.h"
#include <vector>

#include <Eigen/Core>
#include <Eigen/Geometry>

Joint::
Joint()
{
}

Joint::
Joint(const std::string& _name, int _parentIndex, const Eigen::MatrixXd& _transform, const std::vector<Eigen::MatrixXd>& _animList)
{
    name = _name;
    parentIndex = _parentIndex;
    transform = _transform;
    animList = _animList;
}

Joint::
~Joint()
{
}


