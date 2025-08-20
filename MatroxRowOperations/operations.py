# -*- coding: utf-8 -*-
"""
Created on Wed Aug 20 09:20:54 2025

@author: Faith
"""

# from typing import Type
import numpy as np


class Operations:
    _left: np.ndarray = None         # Unsure if I want to use this
    _right: np.ndarray = None        # Unsure if I want to use this
    _aug: np.ndarray = None
    __cut: int = -1

    def __init__(self, left, right):
        # For now, I assume all inputs are numpy arr
        self._left, self._right = left, right
        self._aug = np.hstack([left, right])
        self.__cut = left.shape[1]

        if (self.__cut == -1):
            raise Exception('Error concat')

    def scal(self, row, scalar):
        """Scaling a row (i.e. multiplying or dividing) all elements in a matrix row with a nonzero number."""
        self._aug[row] *= scalar

    def mov(self, row1, row2):
        """Exchange the positions of two matrix rows."""
        self._aug[[row1, row2]] = self._aug[[row2, row1]]

    def add(self, row1, row2, alpha=1.0):
        """Adding a scaled row to/from another row."""
        self._aug[row2] += self._aug[row1] * alpha

    def sub(self, row1, row2, alpha):
        """Subtracting a scaled row to/from another row."""
        self._aug[row2] -= self._aug[row1] * alpha

    def display(self):
        """Display the current augmented matrix."""
        al, ar = self._aug[:, :self.__cut], self._aug[:, self.__cut:]

        def format_matrix(matrix):
            return '\n'.join([' '.join([f'{x:7.3f}' for x in row])
                             for row in matrix])

        print("\n".join(f"{line.ljust(max(len(t.split()[0]) for t in format_matrix(al).split('\n')))} | {r_line}"
                        for line, r_line in zip(format_matrix(al).split('\n'),
                                                format_matrix(ar).split('\n'))))
        print()

    def full(self):
        """Display the current augmented matrix without omitting decimals."""
        al, ar = self._aug[:, :self.__cut], self._aug[:, self.__cut:]

        def format_matrix(matrix):
            return '\n'.join([' '.join([f'{x:.16f}' for x in row])
                             for row in matrix])

        print("\n".join(f"{line.ljust(max(len(t.split()[0]) for t in format_matrix(al).split('\n')))} | {r_line}"
                        for line, r_line in zip(format_matrix(al).split('\n'),
                                                format_matrix(ar).split('\n'))))
        print()


if __name__ == '__main__':
    print('Do not call this submodule.')
    exit(1)
