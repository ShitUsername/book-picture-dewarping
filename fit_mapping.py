#!/usr/bin/python
# Copyright 2011 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pylab import *
import sys
import itertools

import pdb

def range_from_disparity(d):
  z = zeros(d.shape)
  ## from http://mathnathan.com/2011/02/03/depthvsdistance/
  z= 348.0/(1091 - d[:])
  return z

## '#51c373', '#ea6949', '#a370ff' -> original 'G. color block rip-off' palette
gucci_dict = {'red': ((0.0, 0x51/255., 0x51/255.,),
                      (0.5, 0xea/255., 0xea/255.,),
                      (1.0, 0xa3/255., 0xa3/255.,),),
              'green': ((0.0, 0xc3/255., 0xc3/255.,),
                        (0.5, 0xc3/255., 0xc3/255.,),
                        (1.0, 0x70/255., 0x70/255.,),),
              'blue': ((0.0, 0x73/255., 0x73/255.,),
                       (0.5, 0xb5/255., 0xb5/255.,),
                       (1.0, 0xff/255., 0xff/255.,),),
             }

class IntrinsicParameters:
  def __init__(self, f, center):
    self.f = f
    self.center = center

  ## The magical formula that gives distance form the disparity. This is the
  ## theoretical perfect model, a x**-1 expression.
  def distance_from_disparity(self, d):
    return 348.0 / (1091.5 - d)


  def coordinates_from_disparity(self, disparity):
    ## Calculate the world coordinates of each pixel.

    ## Initialize the output matrix with pixel coordinates over image plane, on
    ## camera reference frame.
    output = zeros((disparity.shape[0]*disparity.shape[1], 3))
    output[:,:2] = mgrid[:disparity.shape[1],:disparity.shape[0]].T.reshape(-1,2) - self.center
    output[:,2] = self.f

    ## Calculate z from disparity
    z = self.distance_from_disparity(disparity.ravel())

    #pdb.set_trace()
    output[:,0] *= z / output[:,2]
    output[:,1] *= z / output[:,2]
    output[:,2] = z
    return output

class SquareMesh:
  def __init__(self, disparity, intparam):
    self.disparity = disparity
    self.intparam = intparam
    Np = self.disparity.shape[0]*self.disparity.shape[1]

  def generate_xyz_mesh(self):
    self.xyz = self.intparam.coordinates_from_disparity(self.disparity)

if __name__ == '__main__':

  ion()

  register_cmap(name='guc', data=gucci_dict)
  # rc('image', cmap='RdBu')
  rc('image', cmap='guc')

  ## Check number of parameters
  if len(sys.argv)<2:
    raise Exception('''Incorrect number of parameters.

Usage: %s <data_path>'''%(sys.argv[0]))

  ## Gete the name of directory that contains the data.
  data_path = '%s/'%(sys.argv[1])

  print data_path+'params.txt'
  print data_path+'disparity.txt'

  # [f, p[0], p[1], p[2], theta, phi, psi, k]
  params_file = loadtxt(data_path+'params.txt')
  disparity = loadtxt(data_path+'disparity.txt')




  #imshow(mgrid[:100,:100][0])
  imshow(disparity, interpolation='nearest')

  ran = range_from_disparity(disparity)

  ## Plots the z values
  figure(1)
  imshow(ran, interpolation='nearest')

  #mypar = IntrinsicParameters(300, array([200,200]))
  mypar = IntrinsicParameters(params_file[0], (array(disparity.shape)+1.0)/2)
  sqmesh = SquareMesh(disparity, mypar)
  sqmesh.generate_xyz_mesh()

  import mpl_toolkits.mplot3d.axes3d as p3

  fig=figure(2)
  ax = p3.Axes3D(fig)
  x,y,z = sqmesh.xyz.T
  x = x.reshape(disparity.shape)
  y = y.reshape(disparity.shape)
  z = z.reshape(disparity.shape)

  ## For debugging, just use iamge coordinates "r and s" for x and y, and the disparity for z.
  # x,y = mgrid[:disparity.shape[0],:disparity.shape[1]]
  # z = disparity

  P = 6
  x = x[::P,::P]
  y = y[::P,::P]
  z = z[::P,::P]

  ax.plot_wireframe(x,y,z)
  ax.axis('equal')
