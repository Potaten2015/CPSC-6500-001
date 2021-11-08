import numpy as np
import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from itertools import product, combinations


def deg_2_rad(angle):
    return angle * math.pi / 180

def create_rotation_matrices(x_rotation, y_rotation, z_rotation):
    x_rotation_radians = deg_2_rad(x_rotation)
    y_rotation_radians = deg_2_rad(y_rotation)
    z_rotation_radians = deg_2_rad(z_rotation)

    x_rotation_matrix = np.array([
        [1, 0, 0],
        [0, np.cos(x_rotation_radians), -np.sin(x_rotation_radians)],
        [0, np.sin(x_rotation_radians), np.cos(x_rotation_radians)]
    ])

    y_rotation_matrix = np.array([
        [np.cos(y_rotation_radians), 0, -np.sin(y_rotation_radians)],
        [0, 1, 0],
        [np.sin(y_rotation_radians), 0, np.cos(y_rotation_radians)]
    ])

    z_rotation_radians = np.array([
        [np.cos(z_rotation_radians), -np.sin(z_rotation_radians), 0],
        [np.sin(z_rotation_radians), np.cos(z_rotation_radians), 0],
        [0, 0, 1]
    ])

    return x_rotation_matrix, y_rotation_matrix, x_rotation_matrix




if __name__ == '__main__':
    print_hi('PyCharm')

