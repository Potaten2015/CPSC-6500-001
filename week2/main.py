"""
Robotics
Assignment 2
Author: Taten H. Knight

Summary:        Script shows the beginning and end position of the robot described in the assignment 2 prompt.
                There is an extra vector included at the end of the robot to represent the end effector.

Assumptions:    Linkages between joints are one unit long. End effector is one unit long.

Notes:          This whole script can be made much cleaner by breaking down the sequential transformation of vectors
                into a function.
                It can be even further broken up into a 'robot' class that takes an arbitrary sequence of links
                and joints and their relative orientations, and creates the appropriate transformation matrices.
                This class could also take inputs and output the final position of the robot.
"""

import numpy as np
import math
import matplotlib.pyplot as plt


def deg_2_rad(angle):
    return angle * math.pi / 180


def create_transformation_matrix(x_rotation, y_rotation, z_rotation, x_displacement, y_displacement, z_displacement):
    x_rotation_radians = deg_2_rad(x_rotation)
    y_rotation_radians = deg_2_rad(y_rotation)
    z_rotation_radians = deg_2_rad(z_rotation)

    x_rotation_matrix = np.array([
        [1, 0, 0, 0],
        [0, np.cos(x_rotation_radians), -np.sin(x_rotation_radians), 0],
        [0, np.sin(x_rotation_radians), np.cos(x_rotation_radians), 0],
        [0, 0, 0, 1]
    ])

    y_rotation_matrix = np.array([
        [np.cos(y_rotation_radians), 0, -np.sin(y_rotation_radians), 0],
        [0, 1, 0, 0],
        [np.sin(y_rotation_radians), 0, np.cos(y_rotation_radians), 0],
        [0, 0, 0, 1]
    ])

    z_rotation_matrix = np.array([
        [np.cos(z_rotation_radians), -np.sin(z_rotation_radians), 0, 0],
        [np.sin(z_rotation_radians), np.cos(z_rotation_radians), 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])

    total_rotation_matrix = np.matmul(np.matmul(x_rotation_matrix, y_rotation_matrix), z_rotation_matrix)
    total_rotation_matrix[0][3] = x_displacement
    total_rotation_matrix[1][3] = y_displacement
    total_rotation_matrix[2][3] = z_displacement

    return total_rotation_matrix


def spread_coordinates(coords):
    coord_one = []
    coord_two = []
    coord_three = []
    coord_four = []

    for coord in coords:
        coord_one.append(coord[0])
        coord_two.append(coord[1])
        coord_three.append(coord[2])
        coord_four.append(coord[3])

    return coord_one, coord_two, coord_three, coord_four


def line_creator(x, y, z, u, v, w):
    x_pairs = []
    y_pairs = []
    z_pairs = []
    for i in range(len(x)):
        x_pairs.append((*x[i], *u[i]))
        y_pairs.append((*y[i], *v[i]))
        z_pairs.append((*z[i], *w[i]))

    return x_pairs, y_pairs, z_pairs


if __name__ == '__main__':
    origin = np.array([[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]])  # origin point
    x_0 = 5
    y_0 = 5
    z_0 = 1
    v_1 = np.array([
        [x_0],
        [y_0],
        [z_0]
    ])

    # NOTE: These values are in their respective coordinate frames and need to be transformed to C_0
    original_arm_0 = [[0], [0], [1], [1]]
    original_arm_1 = [[1], [0], [0], [1]]
    original_arm_2 = [[1], [0], [0], [1]]
    original_arm_3 = [[1], [0], [0], [1]]

    # This section finds the position of the original robot
    three_to_two_matrix_start = create_transformation_matrix(0, 0, 0, 1, 0, 0)
    two_to_one_matrix_start = create_transformation_matrix(0, 0, 0, 1, 0, 0)
    one_to_zero_matrix_start = create_transformation_matrix(-90, 0, 0, 0, 0, 1)
    base_rotation_matrix_start = create_transformation_matrix(0, 0, 0, 0, 0, 0)
    arm_0_original_start = np.matmul(
        base_rotation_matrix_start,
        original_arm_0)
    arm_0_original_origin = np.array([[0], [0], [0], [0]])
    arm_1_original_start = np.matmul(
        base_rotation_matrix_start,
        np.matmul(
            one_to_zero_matrix_start,
            original_arm_1))
    arm_1_original_origin = np.array(arm_0_original_start)
    arm_2_original_start = np.matmul(
        base_rotation_matrix_start,
        np.matmul(
            one_to_zero_matrix_start,
            np.matmul(
                two_to_one_matrix_start,
                original_arm_2)))
    arm_2_original_origin = arm_1_original_start
    arm_3_original_start = np.matmul(
        base_rotation_matrix_start,
        np.matmul(
            one_to_zero_matrix_start,
            np.matmul(
                two_to_one_matrix_start,
                np.matmul(
                    three_to_two_matrix_start,
                    original_arm_3))))
    arm_3_original_origin = arm_2_original_start

    x_start, y_start, z_start, extra_one = spread_coordinates([arm_0_original_origin,
                                                               arm_1_original_origin,
                                                               arm_2_original_origin,
                                                               arm_3_original_origin])
    u_start, v_start, w_start, extra_two = spread_coordinates([arm_0_original_start,
                                                               arm_1_original_start,
                                                               arm_2_original_start,
                                                               arm_3_original_start])

    x_pairs_start, y_pairs_start, z_pairs_start = line_creator(x_start, y_start, z_start, u_start, v_start, w_start)

    # This section finds the final position of the robot
    # I added a section to show the end effector vector.
    three_to_two_matrix_final = create_transformation_matrix(0, 0, 0, 1, 0, 0)
    # The z-rotation for each of these is negative because we are transforming into the original frame of reference
    # In this case, this is the equivalent of transposing / inverting the rotation matrix
    two_to_one_matrix_final = create_transformation_matrix(0, 0, -60, 1, 0, 0)
    one_to_zero_matrix_final = create_transformation_matrix(-90, 0, -30, 0, 0, 1)
    # This base rotation matrix applies a rotation in the original frame of reference
    # The angle is positive because we are not transforming into another system
    base_rotation_matrix_final = create_transformation_matrix(0, 0, 15, 0, 0, 0)

    arm_0_final_start = np.matmul(
        base_rotation_matrix_final,
        original_arm_0)
    arm_0_final_origin = np.array([[0], [0], [0], [0]])
    arm_1_final_start = np.matmul(
        base_rotation_matrix_final,
        np.matmul(
            one_to_zero_matrix_final,
            original_arm_1))
    arm_1_final_origin = np.array(arm_0_final_start)
    arm_2_final_start = np.matmul(
        base_rotation_matrix_final,
        np.matmul(
            one_to_zero_matrix_final,
            np.matmul(
                two_to_one_matrix_final,
                original_arm_2)))
    arm_2_final_origin = arm_1_final_start
    arm_3_final_start = np.matmul(
        base_rotation_matrix_final, np.matmul(
            one_to_zero_matrix_final,
            np.matmul(
                two_to_one_matrix_final,
                np.matmul(
                    three_to_two_matrix_final,
                    original_arm_3))))
    arm_3_final_origin = arm_2_final_start

    x_final, y_final, z_final, extra_one = spread_coordinates([arm_0_final_origin,
                                                               arm_1_final_origin,
                                                               arm_2_final_origin,
                                                               arm_3_final_origin])
    u_final, v_final, w_final, extra_two = spread_coordinates([arm_0_final_start,
                                                               arm_1_final_start,
                                                               arm_2_final_start,
                                                               arm_3_final_start])

    x_pairs_final, y_pairs_final, z_pairs_final = line_creator(x_final, y_final, z_final, u_final, v_final, w_final)

    plt.figure('POSITION OF THE ROBOT')
    ax = plt.axes(projection='3d')
    ax.set_title('Robot position before and after movement')
    # ax.quiver(x, y, z, u, v, w)
    for i in range(len(x_pairs_start)):
        ax.plot3D(x_pairs_start[i], y_pairs_start[i], z_pairs_start[i])
    for i in range(len(x_pairs_final)):
        ax.plot3D(x_pairs_final[i], y_pairs_final[i], z_pairs_final[i])
    ax.axes.set_xlim3d(left=-5, right=5)
    ax.axes.set_ylim3d(bottom=-5, top=5)
    ax.axes.set_zlim3d(bottom=-5, top=5)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')

    plt.show()

