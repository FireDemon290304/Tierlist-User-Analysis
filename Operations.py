# -*- coding: utf-8 -*-
"""
Created on Wed Aug 20 09:20:54 2025

@author: Faith
"""

# from typing import Type
import numpy as np


class Operations:
    left: np.ndarray = None         # Unsure if I want to use this
    right: np.ndarray = None        # Unsure if I want to use this
    aug: np.ndarray = None
    cut: int = -1

    def __init__(self, left, right):
        """
        For now, I assume all inputs are numpy arr
        """
        self.left, self.right = left, right
        self.aug = np.hstack([left, right])
        self.cut = left.shape[1]

        if (self.cut == -1):
            raise Exception('Error concat')

    def scal():
        """
        Scaling a row (i.e. multiplying or dividing) all elements in a matrix row with a nonzero number.
        """
        pass

    def mov():
        """
        Exchange the positions of two matrix rows.
        """
        pass

    def add():
        """
        Adding (or subtracting) a scaled row to/from another row.
        """
        pass

    def display(self):
        """Display the current augmented matrix."""
        al, ar = self.aug[:, :self.cut], self.aug[:, self.cut:]

        def format_matrix(matrix):
            return '\n'.join([' '.join([f'{x:1.0f}' for x in row])
                             for row in matrix])

        print("\n".join(f"{line.ljust(max(len(t.split()[0]) for t in format_matrix(al).split('\n')))} | {r_line}"
                        for line, r_line in zip(format_matrix(al).split('\n'),
                                                format_matrix(ar).split('\n'))))


"""
Goal:
    CLI
    - Display
    - Interact

Interact:
    - Call from cli
    - Display
"""
