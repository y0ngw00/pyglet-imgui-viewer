#!/usr/bin/env bash
export CENVDIR=$(pwd)/c_env

mkdir build
cd build
cmake -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_PREFIX_PATH=$CENVDIR \
      -DPYTHON_EXECUTABLE:FILEPATH=/home/imo/anaconda3/envs/GrpDnce/bin/python \
      -DFCL_INCLUDE_DIRS=$CENVDIR/include/fcl \
      -DFCL_LIBRARIES=$CENVDIR/lib/libfcl.so \
      -DFBX_INCLUDE_DIRS=$CENVDIR/include/fbxsdk \
      -DFBX_LIBRARIES=$CENVDIR/lib/libfbxsdk.so \
      -DCCD_INCLUDE_DIRS=$CENVDIR/include/ccd \
      -DCCD_LIBRARIES=$CENVDIR/lib/libccd.so \
       ..
cd ..
