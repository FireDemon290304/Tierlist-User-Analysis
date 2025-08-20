# -*- coding: utf-8 -*-
"""
Created on Wed Aug 20 09:13:50 2025

@author: Faith
"""

from operations import Operations
import numpy as np
import sys


A = np.array([
    [1, 0],
    [0, 1]
], dtype=float)
B = np.array([
    [1],
    [2]
], dtype=float)

help_str = 'help'
opr = Operations(A, B)


def inp(cmd):
    parts = cmd.strip().lower().split()
    if not parts:
        raise Exception('Input Error')

    op = parts[0]

    match op:
        # For now, assume everything works. It won't crash anyway, there's a catch.
        # - 1 for align
        case 'swap' | 's':
            opr.mov(int(parts[1]) - 1, int(parts[2]) - 1)
        case 'scale' | 'x':
            opr.scal(int(parts[1]) - 1, float(parts[2]))
        case 'add':
            opr.add(int(parts[1]) - 1, int(parts[2]) - 1, float(parts[3]))
        case 'sub':
            opr.sub(int(parts[1]) - 1, int(parts[2]) - 1, float(parts[3]))
        case 'full' | 'f':
            opr.full()
        case 'exit' | 'e' | 'quit' | 'q':
            sys.exit(0)
        case 'help' | 'h':
            print(help_str)
        case _:
            print('Bad input. Try "Help"')


def main():
    print('Initial:')
    opr.display()

    while True:
        try:
            inp(input('> '))
        except Exception as e:
            print(f'Error:{e}\n')
        except KeyboardInterrupt:
            print('exit')
            sys.exit(0)
        opr.display()


if __name__ == '__main__':
    main()
else:
    print('Do not call this as a submodule. This should (for now) be a main-only file')
    exit(1)
