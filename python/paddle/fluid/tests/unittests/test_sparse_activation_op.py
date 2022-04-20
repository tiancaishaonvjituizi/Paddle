# Copyright (c) 2022 PaddlePaddle Authors. All Rights Reserved.
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

from __future__ import print_function
import unittest
import numpy as np
import paddle
from paddle.fluid.framework import _test_eager_guard


class TestSparseActivation(unittest.TestCase):
    def test_sparse_relu(self):
        with _test_eager_guard():
            x = [[0, -1, 0, 2], [0, 0, -3, 0], [4, 5, 0, 0]]

            def dense_relu(x):
                dense_x = paddle.to_tensor(
                    x, dtype='float32', stop_gradient=False)
                dense_relu = paddle.nn.ReLU()
                dense_out = dense_relu(dense_x)
                dense_out.backward(dense_out)
                return dense_out, dense_x.grad

            dense_x = paddle.to_tensor(x, dtype='float32', stop_gradient=False)
            sparse_dim = 2
            sparse_x = dense_x.to_sparse_coo(sparse_dim)
            sparse_relu = paddle.sparse.ReLU()
            sparse_out = sparse_relu(sparse_x)
            sparse_out.backward(sparse_out)

            dense_out, dense_x_grad = dense_relu(x)
            assert np.array_equal(dense_out.numpy(),
                                  sparse_out.to_dense().numpy())
            assert np.array_equal(dense_x_grad.numpy(),
                                  sparse_x.grad.to_dense().numpy())

    def test_sparse_coo_sqrt(self):
        with _test_eager_guard():
            x = [[0, 4, 0, 2], [0, 0, 16, 0]]
            dense_x = paddle.to_tensor(x, dtype='float32')
            sparse_dim = 2
            sparse_coo_x = dense_x.to_sparse_coo(sparse_dim)
            sparse_act_out = _C_ops.final_state_sparse_coo_sqrt(sparse_coo_x)
            correct_result = [2, np.sqrt(2), 4]
            actual_result = sparse_act_out.non_zero_elements().numpy()
            assert np.allclose(correct_result, actual_result)

    def test_sparse_csr_sqrt(self):
        with _test_eager_guard():
            x = [[0, 4, 0, 2], [0, 0, 0, 0], [0, 0, 16, 0]]
            dense_x = paddle.to_tensor(x, dtype='float32')
            sparse_coo_x = dense_x.to_sparse_csr()
            sparse_act_out = _C_ops.final_state_sparse_csr_sqrt(sparse_coo_x)
            correct_result = [2, np.sqrt(2), 4]
            actual_result = sparse_act_out.non_zero_elements().numpy()
            assert np.allclose(correct_result, actual_result)


if __name__ == "__main__":
    unittest.main()
