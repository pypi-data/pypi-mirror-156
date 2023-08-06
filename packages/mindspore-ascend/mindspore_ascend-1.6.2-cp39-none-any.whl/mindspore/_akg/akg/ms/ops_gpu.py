# Copyright 2021 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""GPU operators"""
import akg.utils as utils
import akg.ops.array.gpu as array
import akg.ops.nn.gpu as nn

def Squeeze(x, axis=None, target=utils.CUDA):
    """Squeeze"""
    return array.Squeeze(x, axis, target)

def SqueezeGrad(y_grad, x_shape, target=utils.CUDA):
    """SqueezeGrad"""
    return array.SqueezeGrad(y_grad, x_shape, target)

def ReLU6(x, target=utils.CUDA):
    """ReLU6"""
    return nn.ReLU6(x, target)

def ReLU6Grad(y_grad, x, target=utils.CUDA):
    """ReLU6Grad"""
    return nn.ReLU6Grad(y_grad, x, target)

def HSwish(x, target=utils.CUDA):
    """HSwish"""
    return nn.HSwish(x, target)

def HSwishGrad(y_grad, x, target=utils.CUDA):
    """HSwishGrad"""
    return nn.HSwishGrad(y_grad, x, target)

def HSigmoid(x, target=utils.CUDA):
    """HSigmoid"""
    return nn.HSigmoid(x, target)

def HSigmoidGrad(y_grad, x, target=utils.CUDA):
    """HSigmoidGrad"""
    return nn.HSigmoidGrad(y_grad, x, target)

