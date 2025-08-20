# -*- coding: utf-8 -*-
"""
Created on Wed Aug 20 09:13:50 2025

@author: Faith
"""

from Operations import Operations
import numpy as np


def main():
    # TODO: make CLI

    A = np.array([
        [1, 0],
        [0, 1]
    ])
    B = np.array([
        [1],
        [2]
    ])

    Operations(A, B).display()


if __name__ == '__main__':
    main()
else:
    print('Do not call this as a submodule. This should (for now) be a main-only file')
