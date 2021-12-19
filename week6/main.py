"""
Week 6 Assignment: Jacobian Matrix using DHT
Author: Taten H. Knight
Date: 2021.12.18

Notes:
    - This program calculates the symbolic representation of the jacobian matrix for a spherical manipulator by taking
    advantage of the sympy and numppy packages
    - We can substitute out the symbols for values and find the solution to the matrices using the sub_and_solve
    function
"""


import numpy as np
from sympy import Symbol, sin, pprint, cos, Float, log, Matrix, shape, simplify

# define Symbolic variables
theta1 = Symbol('theta_1')
theta2 = Symbol('theta_2')
a1 = Symbol('a_1')
a2 = Symbol('a_2')
a3 = Symbol('a_3')
d1 = Symbol('d_1')


def symbolic_dh_table():
    dh_row_1 = np.array([theta1 - 90, -90, 0, a1])
    dh_row_2 = np.array([0, 0, 0, a2])
    dh_row_3 = np.array([0, 0, 0, d1 + a3])
    dh_table = np.array([dh_row_1, dh_row_2, dh_row_3])
    return dh_table


def symbolic_frame_htms(dh_table):
    htm_matrices = []
    for row in dh_table:
        htm_matrix = np.array([
            [cos(row[0]), -sin(row[0]) * cos(row[1]), sin(row[0]) * sin(row[1]), row[2] * cos(row[0])],
            [sin(row[0]), cos(row[0]) * cos(row[1]), -cos(row[0]) * sin(row[1]), row[2] * sin(row[0])],
            [0, sin(row[1]), cos(row[1]), row[3]],
            [0, 0, 0, 1]
        ])
        htm_matrices.append(htm_matrix)
    return htm_matrices


def symbolic_origin_htms(frame_htms):
    final_htm = np.identity(4)
    origin_htms = []
    for htm in frame_htms:
        final_htm = final_htm @ htm
        origin_htms.append(final_htm)
    return origin_htms


def symbolic_jacobians(origin_htms):
    js = []
    for i in range(1, len(origin_htms) + 1):
        # print('\n\n\n')
        # pprint(simplify(origin_htms[i - 1][:, 3]))
        if i == 1:
            z_minus = np.array([[0], [0], [1]])
            o_minus = np.array([[0], [0], [0]])
        else:
            z_minus = origin_htms[i - 1][:3, :3] @ np.array([[0], [0], [1]])
            o_minus = (origin_htms[i - 1] @ np.array([[0], [0], [0], [1]]))[0:3]
        on = (origin_htms[-1] @ np.array([[0], [0], [0], [1]]))[0:3]
        for j, value in enumerate(z_minus):
            z_minus[j] = simplify(value)
        for j, value in enumerate(o_minus):
            o_minus[j] = simplify(value)
        for j, value in enumerate(on):
            on[j] = simplify(value)
        # print('z_i-1')
        # pprint(z_minus)
        # print('o_i-1')
        # pprint(o_minus)
        # print('o_n')
        # pprint(on)
        j = np.cross(z_minus.T, (on - o_minus).T)
        for k, value in enumerate(j):
            j[k] = simplify(value)
        # print(f'j_{i}')
        # print(j)
        j = np.append(j, z_minus)
        js.append(j.reshape(6, 1))
    return js


def sub_and_solve(jacobians, d_1=1, a_1=1, a_2=1, a_3=1, theta_1=45):
    theta_1 = np.deg2rad(theta_1)
    jacobians_copy = jacobians.copy()
    for i, jacobian in enumerate(jacobians_copy):
        for j, row in enumerate(jacobian):
            for k, item in enumerate(row):
                try:
                    jacobians_copy[i][j][k] = ((jacobians[i][j][k]).subs([(d1, d_1), (a1, a_1), (a2, a_2), (a3, a_3), (theta1, theta_1)])).evalf()
                except:
                    pass
    return jacobians_copy


def run():
    symbolic_dh = symbolic_dh_table()
    # pprint(symbolic_dh)
    frame_htm_matrices = symbolic_frame_htms(symbolic_dh)
    # pprint(frame_htm_matrices)
    origin_htms = symbolic_origin_htms(frame_htm_matrices)
    # pprint(origin_htms)
    jacobians = symbolic_jacobians(origin_htms)
    for i, jacobian in enumerate(jacobians):
        for j, row in enumerate(jacobian):
            for k, item in enumerate(row):
                try:
                    jacobians[i][j][k] = simplify(item.subs(cos(theta1 - 90), sin(theta1)).subs(sin(theta1 - 90), -cos(theta1)).subs(sin(90), 1).subs(cos(90), 0))
                except:
                    pass
    for i, jacobian in enumerate(jacobians):
        print(f'\nJ_{i+1}')
        pprint(jacobian)
    solved = sub_and_solve(jacobians)
    pprint(solved)

if __name__ == '__main__':
    run()