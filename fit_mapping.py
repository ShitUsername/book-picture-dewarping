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


import mpl_toolkits.mplot3d.axes3d as p3


import pdb

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
    ## "identity" version
    #return 1/(d/1e3)
    # return 3e2-1./(d/5e1) ## for cone-00
    # return 2-1./(d/5e3) ## for trig-00
    return 2-1./(d/5e1) ## for trig-00
    # return 1000-1/(d/1e5)
    ## Correct version, inverse of the function from http://mathnathan.com/2011/02/03/depthvsdistance/
    ## return 348.0 / (1091.5 - d)


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
    output[:,0] *= z / self.f
    output[:,1] *= z / self.f
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




  fig = plt.figure(figsize=plt.figaspect(.5))
  fig.suptitle('Calculation of 3D coordinates from range data (with quantization)', fontsize=20, fontweight='bold')

  ax = fig.add_subplot(1,2,1)
  #p3.Axes3D(fig, rect = [.05, .2, .4, .6])

  title('Kinect data (disparity)', fontsize=16)

  cax = ax.imshow(disparity, interpolation='nearest')
  #colorbar(cax)

  #mypar = IntrinsicParameters(300, array([200,200]))
  mypar = IntrinsicParameters(params_file[0], .5*(1+array([disparity.shape[1], disparity.shape[0]])))
  sqmesh = SquareMesh(disparity, mypar)
  sqmesh.generate_xyz_mesh()


  ax = p3.Axes3D(fig, rect = [.55, .2, .4, .6], aspect='equal')
  title('Square mesh on 3D space', fontsize=16)
  x,y,z = sqmesh.xyz.T
  x = x.reshape(disparity.shape)
  y = y.reshape(disparity.shape)
  z = z.reshape(disparity.shape)

  ## For debugging, just use image coordinates "r and s" for x and y, and the disparity for z.
  #x,y = mgrid[:disparity.shape[0],:disparity.shape[1]]
  #z = disparity

  P = 12
  x = x[::P,::P]
  y = y[::P,::P]
  z = z[::P,::P]

  ax.axis('equal')
  ax.plot_wireframe(x,y,z)

  mrang = max([x.max()-x.min(), y.max()-y.min(), z.max()-z.min()])/2
  midx = (x.max()+x.min())/2
  midy = (y.max()+y.min())/2
  midz = (z.max()+z.min())/2
  ax.set_xlim3d(midx-mrang, midx+mrang)
  ax.set_ylim3d(midy-mrang, midy+mrang)
  ax.set_zlim3d(midz-mrang, midz+mrang)