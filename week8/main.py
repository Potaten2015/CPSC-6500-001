"""
Week 8 Assignment: Re-write
Author: Taten H. Knight
Date: 2021.12.19

Notes:
    - Definitely struggled to solve for the final joint variables using inverse kinematics. The first half made sense
    but the wrist I struggled with. Sorry, thank you for a good course. Going to keep the material from Github for
    the future
"""


import numpy as np
import numpy.linalg as la
from pprint import pprint
import sympy as sym
from sympy import sin as s, cos as c, pprint as pp


a1 = sym.Symbol('a_1')
a2 = sym.Symbol('a_2')
a3 = sym.Symbol('a_3')
a4 = sym.Symbol('a_4')
a5 = sym.Symbol('a_5')
a6 = sym.Symbol('a_6')
a7 = sym.Symbol('a_7')
t2 = sym.Symbol('theta_2')
t4 = sym.Symbol('theta_4')
t5 = sym.Symbol('theta_5')
t6 = sym.Symbol('theta_6')
d1 = sym.Symbol('d_1')
d3 = sym.Symbol('d_3')


def run():
    # HTMs
    h_3_0 = np.array([
        [-s(t2), 0, c(t2), (a3 + a4 + d3) * c(t2)],
        [c(t2), 0, s(t2), (a3 + a4 + d3) * s(t2)],
        [0, 1, 0, a1 + a2 + d1],
        [0, 0, 0, 1]
    ])

    h_6_3 = np.array([
        [-c(t4)*s(t5)*c(t6)+s(t4)*s(t6), c(t4)*s(t5)*s(t6)+s(t4)*c(t6), c(t4)*c(t5), (a6+a7)*c(t5)*c(t5)],
        [-s(t4)*s(t5)*c(t6)-c(t4)*s(t6), s(t4)*s(t5)*s(t6)+c(t4)*c(t6), s(t4)*c(t5), (a6+a7)*s(t5)*c(t5)],
        [c(t5)*c(t6), -c(t5)*s(t6), s(t5), (a6+a7)*s(t5)+a5],
        [0, 0, 0, 1]
    ])
    h_6_0 = h_3_0 @ h_6_3

    # Rotation Matrices
    r_3_0 = (h_3_0 @ np.array([[0], [0], [1]]))[0:3]
    r_6_3 = (h_6_3 @ np.array([[0], [0], [1]]))[0:3]
    r_6_0 = (h_6_0 @ np.array([[0], [0], [1]]))[0:3]


def cylinder_joints(x, y, z, a1, a2, a3, a4):
    pass



if __name__ == '__main__':
    run()