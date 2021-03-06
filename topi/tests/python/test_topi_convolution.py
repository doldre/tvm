"""Example code to do convolution."""
import os
import numpy as np
import tvm
import topi
from topi.util import get_const_tuple


def verify_convolution(batch, in_size, in_channel, num_filter, kernel, stride, padding):
    in_height = in_width = in_size

    with topi.target.rasp():
        A = tvm.placeholder((batch, in_channel, in_height, in_width), name='A')
        W = tvm.placeholder((num_filter, in_channel, kernel, kernel), name='W')
        B = topi.nn.convolution(A, W, stride, padding)
    s = topi.rasp.schedule_convolution([B])

    a_np = np.random.uniform(size=get_const_tuple(A.shape)).astype(A.dtype)
    w_np = np.random.uniform(size=get_const_tuple(W.shape)).astype(W.dtype)
    b_np = topi.testing.conv2d_nchw_python(a_np, w_np, stride, padding)

    ctx = tvm.cpu(0)
    a = tvm.nd.array(a_np, ctx)
    w = tvm.nd.array(w_np, ctx)
    b = tvm.nd.array(np.zeros(get_const_tuple(B.shape), dtype=B.dtype), ctx)
    func = tvm.build(s, [A, W, B], "llvm")
    func(a, w, b)
    np.testing.assert_allclose(b.asnumpy(), b_np, rtol=1e-5)

def test_convolution():
    verify_convolution(1, 56,  64, 64,  3, 1, 1)

if __name__ == "__main__":
    test_convolution()
