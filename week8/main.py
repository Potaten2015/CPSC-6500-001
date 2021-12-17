import numpy as np
import numpy.linalg as la
from pprint import pprint


def run():
    r_3_0 = np.array([
        [0.25, -0.71, 0.66],
        [0.48, -0.86, -0.17],
        [0.88, 0.48, 0.03]
    ])

    r_6_0 = np.array([
        [0.04, 0.93, 0.29],
        [-0.65, 0.45, 0.53],
        [0.45, -0.47, 0.83]
    ])

    r_6_3 = la.inv(r_3_0) @ r_6_0

    pprint(r_6_3)


def run2():
    r_3_0 = np.array([
        [0.33, -0.91, 0.24],
        [0.93, 0.24, -0.29],
        [0.19, 0.38, 0.90]
    ])

    r_6_0 = np.array([
        [-0.63, 0.29, 0.56],
        [0.65, -0.60, 0.64],
        [0.64, 0.76, 0.13]
    ])

    r_6_3 = la.inv(r_3_0) @ r_6_0

    pprint(r_6_3)


def run3():
    r_3_0 = np.array([
        [0.42, -0.24, 0.87],
        [0.88, -0.47, -0.03],
        [0.47, 0.88, 0.00]
    ])

    r_6_0 = np.array([
        [0.35, 0.55, 0.61],
        [0.01, -0.47, 0.73],
        [0.98, -0.52, -0.11]
    ])

    r_6_3 = la.inv(r_3_0) @ r_6_0

    pprint(r_6_3)


if __name__ == '__main__':
    # run()
    # run2()
    run3()