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

"""operator dsl function: CSRMV"""
import akg.tvm
from akg.utils import validation_check as vc_util
from akg.composite import csrmv as cuda_csrmv

@vc_util.check_input_type(akg.tvm.tensor.Tensor, akg.tvm.tensor.Tensor,
                          akg.tvm.tensor.Tensor, akg.tvm.tensor.Tensor)
def CSRMV(data, indices, indptr, weight):
    return cuda_csrmv((indptr, indices, data, weight), {})
