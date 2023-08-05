from ccc.coef.impl import *

try:
    # Run CCC to initialize/compile its functions with numba
    ccc(np.random.rand(10), np.random.rand(10))
except Exception as e:
    raise e
