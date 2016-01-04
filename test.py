# OpenFace tests, run with `nosetests-2.7 -v -d test.py`
#
# Copyright 2015 Carnegie Mellon University
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


import cv2
import os

import numpy as np
np.set_printoptions(precision=2)
from numpy.linalg import norm

import scipy
import scipy.spatial

import openface

from subprocess import Popen, PIPE

fileDir = os.path.dirname(os.path.realpath(__file__))
modelDir = os.path.join(fileDir, 'models')
dlibModelDir = os.path.join(modelDir, 'dlib')
openfaceModelDir = os.path.join(modelDir, 'openface')

dlibFacePredictor = os.path.join(dlibModelDir,
                                 "shape_predictor_68_face_landmarks.dat")
networkModel = os.path.join(openfaceModelDir, 'nn4.v1.t7')
imgDim = 96

align = openface.AlignDlib(dlibFacePredictor)
net = openface.TorchNeuralNet(networkModel, imgDim=imgDim)


def test_pipeline():
    imgPath = os.path.join(fileDir, 'images', 'examples', 'lennon-1.jpg')
    bgrImg = cv2.imread(imgPath)
    if bgrImg is None:
        raise Exception("Unable to load image: {}".format(imgPath))
    rgbImg = cv2.cvtColor(bgrImg, cv2.COLOR_BGR2RGB)
    assert np.isclose(norm(rgbImg), 11.1355)

    bb = align.getLargestFaceBoundingBox(rgbImg)
    assert bb.left() == 341
    assert bb.right() == 1006
    assert bb.top() == 193
    assert bb.bottom() == 859

    alignedFace = align.align(imgDim, rgbImg, bb)
    assert np.isclose(norm(alignedFace), 8.30662)

    rep = net.forward(alignedFace)
    cosDist = scipy.spatial.distance.cosine(rep, np.ones(128))
    assert np.isclose(cosDist, 1.0133943701889758)


def test_compare_demo():
    cmd = ['python2', os.path.join(fileDir, 'demos', 'compare.py'),
           os.path.join(fileDir, 'images', 'examples', 'lennon-1.jpg'),
           os.path.join(fileDir, 'images', 'examples', 'lennon-2.jpg')]
    p = Popen(cmd, stdout=PIPE, stderr=PIPE)
    (out, err) = p.communicate()
    print(err)
    assert "0.352" in out


def test_classification_demo():
    cmd = ['python2', os.path.join(fileDir, 'demos', 'classifier.py'),
           'infer',
           os.path.join(fileDir, 'models', 'openface',
                        'celeb-classifier.nn4.v1.pkl'),
           os.path.join(fileDir, 'images', 'examples', 'carell.jpg')]
    p = Popen(cmd, stdout=PIPE, stderr=PIPE)
    (out, err) = p.communicate()
    print(err)
    assert "Predict SteveCarell with 0.85 confidence." in out
