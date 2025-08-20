# -*- coding: utf-8 -*-
"""
Created on Mon Jul 14 13:08:01 2025

@author: Faith
"""


import numpy as np
from parser import Algos
import timeit

# ------------------------ FOR G-S -------------------

# 2D vectors that are orthogonal
A = np.array([
    [1, 0],
    [0, 1]
])
# Should return same set, already orthonormal

# Second vector is a multiple of the first
B = np.array([
    [1, 2],
    [2, 4]
])
# Should return only one vector

C = np.array([
    [1, 0, 0],
    [0, 1, 0],
    [1, 1, 0]
])
# First two are orthogonal; third is a linear combination -> should return only first two

D = np.array([
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 10]  # LI but not orthogonal
])
# Should return 3 orthonormal vectors

# From danziger/professor/MTH141:
E = np.array([
    [1, 2, 1],
    [1, 1, 3],
    [2, 1, 1]
])
# Should return:
# 1: 1/sqrt6(1, 2, 1)
# 2: 1/sqrt5(0, -1, 2)
# 3: 1/sqrt57(35, -14, 17)

F = np.array([
    [0, 1],
    [1, 1]
])

# CHECK:
# Do: V_i dot v_j = delta_i_j where delta = Kronecker delta (i.e. v dot v.T = I)

test = np.array([[3.0, 1.0], [2.0, 2.0]])
test2 = np.array([[1.0, 1.0, 0.0], [1.0, 3.0, 1.0], [2.0, -1.0, 1.0]])

res = Algos.gram_schmidt_explicit(test2)
res2 = Algos.gram_schmidt_vectorised(test2)
res3 = Algos.gram_schmidt_qr(test2)
# setup_code = '''
# import numpy as np
# from parser import Algos
# matrix = np.array([[1.0, 1.0, 0.0], [1.0, 3.0, 1.0], [2.0, -1.0, 1.0]])
# '''

# t1 = 'Algos.gram_schmidt_explicit(matrix)'
# t2 = 'Algos.gram_schmidt_vectorised(matrix)'

# print(timeit.timeit(t1, setup=setup_code))
# print(timeit.timeit(t2, setup=setup_code))


print(res)
print(res @ res.T)
print()
print(res2)
print(res2 @ res2.T)
print()
print(res3)
print(res3 @ res3.T)


# ----------------------------- FOR SVD --------------------
A = np.eye(3)
# U = I, Σ = I, Vᵗ = I

B = np.array([
    [1, 0],
    [2, 0],
    [3, 0]
])
# Only one non-zero singular value

C = np.array([
    [1, 0],
    [0, 1],
    [1, 1]
])
# 2 singular values > 0, shows 2D column space

D = np.array([
    [3, 2],
    [2, 3]
])
# Diagonal Σ, U and V should be orthogonal
