"""
Week 4 Assignment: Spherical Manipulator
Author: Taten H. Knight
Date: 2021.11.26

Notes:
    - Can use the 'plot' class method with 'axes=True' to visualize the orientation of the axes on scara and speherical
    manipulators.
    - 'Spherical.find_angles' takes in potential x,y,z coordinates and returns the corresponding theta_1, theta_2, ONLY
    if the end-effector can reach the given x,y,z coordinates. This is accomplished by finding the angles via their
    explicit equations, putting those angles into the explicit equation for x,y,z, and comparing the given x,y,z with
    the equation results.
    - 'Spherical.plot_workspace' plots the workspace of the current instance with a given density of angles (resultant
    graph has '# of theta_1 angles' x '# of theta_2 angles' points, where '# theta_1 angles' = '# theta_2 angles' = density.
    Angles are 'np.linspace(0, 359, density)'
    - Future improvements include creating a base 'manipulator' model that generalizes methods for finding HTMs and
    plotting the manipulator positions. Would also like to simulate manipulator motion.
"""


import numpy as np
import matplotlib.pyplot as plt
from pprint import pprint
from matplotlib import cm


def create_orientation_matrix(orientation_array):
    "Takes an array of string like [-x, y, -z] and converts to an orientation matrix"

    def _parse_input(coord):
        if 'x' in coord:
            if '-' in coord:
                return -1, 0
            else:
                return 1, 0
        if 'y' in coord:
            if '-' in coord:
                return -1, 1
            else:
                return 1, 1
        if 'z' in coord:
            if '-' in coord:
                return -1, 2
            else:
                return 1, 2

    orientation_matrix = np.zeros((4, 4))

    for i, val in enumerate(orientation_array):
        orientation_values = _parse_input(val)
        orientation_matrix[orientation_values[1]][i] = orientation_values[0]

    orientation_matrix[3][3] = 1
    return orientation_matrix


def create_rotation_matrix(rotation_axis, degree_angle):
    "Creates rotation matrix with 1 row and 1 column of padding for future HTM multiplication"
    radian_angle = np.deg2rad(degree_angle)

    if 'x' in rotation_axis:
        rotation_matrix = np.array([
            [1, 0, 0, 0],
            [0, np.cos(radian_angle), -np.sin(radian_angle), 0],
            [0, np.sin(radian_angle), np.cos(radian_angle), 0],
            [0, 0, 0, 1]
        ])
    if 'y' in rotation_axis:
        rotation_matrix = np.array([
            [np.cos(radian_angle), 0, np.sin(radian_angle), 0],
            [0, 1, 0, 0],
            [-np.sin(radian_angle), 0, np.cos(radian_angle), 0],
            [0, 0, 0, 1]
        ])
    if 'z' in rotation_axis:
        rotation_matrix = np.array([
            [np.cos(radian_angle), -np.sin(radian_angle), 0, 0],
            [np.sin(radian_angle), np.cos(radian_angle), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
    return rotation_matrix


def create_displacement_vector(vector):
    vector = np.append(vector, 1)
    np.reshape(vector, (4, 1))
    return vector


def create_htm(orientation_matrix, displacement_vector, rotation_matrix=None):
    if rotation_matrix is not None:
        htm = orientation_matrix @ rotation_matrix
    else:
        htm = orientation_matrix
    htm[:, 3] = displacement_vector
    return htm


def create_origin_htm(htms):
    origin_htm = np.identity(4)
    for htm in htms:
        origin_htm = origin_htm @ htm

    return origin_htm


class Scara:
    def __init__(self, link_lengths=[1.0, 1.0, 1.0], effector_length=1.0, rotation_angles=[0.0, 0.0, 0.0],
                 end_effector_displacement=0.0):
        # Frame 0 origin
        self.origin = np.array([[0], [0], [0]])
        # Link lengths
        self.a1 = link_lengths[0]
        self.a2 = link_lengths[1]
        self.a3 = link_lengths[2]
        # End effector length
        self.effector_length = effector_length
        # Joint rotations
        self.theta_1 = np.deg2rad(rotation_angles[0])
        self.theta_2 = np.deg2rad(rotation_angles[1])
        self.theta_3 = np.deg2rad(rotation_angles[2])
        # Effector displacement
        self.d = end_effector_displacement
        # Orientation matrices frame to frame
        self.o_1_0 = create_orientation_matrix(['x', 'y', 'z'])
        self.o_2_1 = create_orientation_matrix(['x', 'y', 'z'])
        self.o_3_2 = create_orientation_matrix(['x', 'y', 'z'])
        self.o_4_3 = create_orientation_matrix(['x', '-y', '-z'])
        # Displacement vectors frame to frame
        self.d_1_0 = create_displacement_vector([0, 0, self.a1])
        self.d_2_1 = create_displacement_vector([self.a2, 0, 0])
        self.d_3_2 = create_displacement_vector([self.a3, 0, 0])
        self.d_4_3 = create_displacement_vector([0, 0, -self.d])
        # Joint rotation matrices
        self.r_1 = create_rotation_matrix('z', rotation_angles[0])
        self.r_2 = create_rotation_matrix('z', rotation_angles[1])
        self.r_3 = create_rotation_matrix('z', rotation_angles[2])
        # Link vectors relative to their original frames
        self.link_1 = np.array([[0], [0], [self.a1], [1]])
        self.link_2 = np.array([[self.a2], [0], [0], [1]])
        self.link_3 = np.array([[self.a3], [0], [0], [1]])
        self.effector = np.array([[0], [0], [self.effector_length], [1]])
        # HTMs frame to frame
        self.htm_1_0 = create_htm(self.o_1_0, self.d_1_0, self.r_1)
        self.htm_2_1 = create_htm(self.o_2_1, self.d_2_1, self.r_2)
        self.htm_3_2 = create_htm(self.o_3_2, self.d_3_2, self.r_3)
        self.htm_4_3 = create_htm(self.o_4_3, self.d_4_3)
        # HTMs to Frame 0
        self.htm_2_0 = create_origin_htm([self.htm_1_0, self.htm_2_1])
        self.htm_3_0 = create_origin_htm([self.htm_2_0, self.htm_3_2])
        self.htm_4_0 = create_origin_htm([self.htm_3_0, self.htm_4_3])
        # Links in Frame 0
        self.link_1_origin = self.link_1
        self.link_2_origin = self.htm_1_0 @ self.link_2
        self.link_3_origin = self.htm_2_0 @ self.link_3
        self.extender_origin = self.htm_4_0 @ np.array([[0], [0], [0], [1]])
        # Final point of end effector in Frame 0
        self.effector_origin = self.htm_4_0 @ self.effector

        # Axes in origin frame
        self.general_x_axis = np.array([[1], [0], [0], [1]])
        self.general_y_axis = np.array([[0], [1], [0], [1]])
        self.general_z_axis = np.array([[0], [0], [1], [1]])
        self.general_origin = np.array([[0], [0], [0], [1]])
        self.f_0_origin = self.general_origin
        self.f_0_x = self.general_x_axis
        self.f_0_y = self.general_y_axis
        self.f_0_z = self.general_z_axis
        self.f_1_origin = self.htm_1_0 @ self.general_origin
        self.f_1_x = np.subtract(self.htm_1_0 @ self.general_x_axis, self.f_1_origin)
        self.f_1_y = np.subtract(self.htm_1_0 @ self.general_y_axis, self.f_1_origin)
        self.f_1_z = np.subtract(self.htm_1_0 @ self.general_z_axis, self.f_1_origin)
        self.f_2_origin = self.htm_2_0 @ self.general_origin
        self.f_2_x = np.subtract(self.htm_2_0 @ self.general_x_axis, self.f_2_origin)
        self.f_2_y = np.subtract(self.htm_2_0 @ self.general_y_axis, self.f_2_origin)
        self.f_2_z = np.subtract(self.htm_2_0 @ self.general_z_axis, self.f_2_origin)
        self.f_3_origin = self.htm_3_0 @ self.general_origin
        self.f_3_x = np.subtract(self.htm_3_0 @ self.general_x_axis, self.f_3_origin)
        self.f_3_y = np.subtract(self.htm_3_0 @ self.general_y_axis, self.f_3_origin)
        self.f_3_z = np.subtract(self.htm_3_0 @ self.general_z_axis, self.f_3_origin)
        self.f_4_origin = self.htm_4_0 @ self.general_origin
        self.f_4_x = np.subtract(self.htm_4_0 @ self.general_x_axis, self.f_4_origin)
        self.f_4_y = np.subtract(self.htm_4_0 @ self.general_y_axis, self.f_4_origin)
        self.f_4_z = np.subtract(self.htm_4_0 @ self.general_z_axis, self.f_4_origin)

        self.x_axis_starts = [self.f_0_origin[0][0], self.f_1_origin[0][0],self.f_2_origin[0][0],
                              self.f_3_origin[0][0], self.f_4_origin[0][0]]
        self.y_axis_starts = [self.f_0_origin[1][0], self.f_1_origin[1][0], self.f_2_origin[1][0],
                              self.f_3_origin[1][0], self.f_4_origin[1][0]]
        self.z_axis_starts = [self.f_0_origin[2][0], self.f_1_origin[2][0], self.f_2_origin[2][0],
                              self.f_3_origin[2][0], self.f_4_origin[2][0]]

        self.x_axis_x_ends = [self.f_0_x[0][0], self.f_1_x[0][0], self.f_2_x[0][0], self.f_3_x[0][0], self.f_4_x[0][0]]
        self.x_axis_y_ends = [self.f_0_x[1][0], self.f_1_x[1][0], self.f_2_x[1][0], self.f_3_x[1][0], self.f_4_x[1][0]]
        self.x_axis_z_ends = [self.f_0_x[2][0], self.f_1_x[2][0], self.f_2_x[2][0], self.f_3_x[2][0], self.f_4_x[2][0]]

        self.y_axis_x_ends = [self.f_0_y[0][0], self.f_1_y[0][0], self.f_2_y[0][0], self.f_3_y[0][0], self.f_4_y[0][0]]
        self.y_axis_y_ends = [self.f_0_y[1][0], self.f_1_y[1][0], self.f_2_y[1][0], self.f_3_y[1][0], self.f_4_y[1][0]]
        self.y_axis_z_ends = [self.f_0_y[2][0], self.f_1_y[2][0], self.f_2_y[2][0], self.f_3_y[2][0], self.f_4_y[2][0]]

        self.z_axis_x_ends = [self.f_0_z[0][0], self.f_1_z[0][0], self.f_2_z[0][0], self.f_3_z[0][0], self.f_4_z[0][0]]
        self.z_axis_y_ends = [self.f_0_z[1][0], self.f_1_z[1][0], self.f_2_z[1][0], self.f_3_z[1][0], self.f_4_z[1][0]]
        self.z_axis_z_ends = [self.f_0_z[2][0], self.f_1_z[2][0], self.f_2_z[2][0], self.f_3_z[2][0], self.f_4_z[2][0]]

    def plot(self, figure_name="Scara Plot", axes=False, axes_length=1):
        # Plot the location of robot with current configuration
        plt.figure(figure_name)
        ax = plt.axes(projection='3d')
        ax.axes.set_xlim3d(left=-(self.a2 + self.a3 + 1), right=(self.a2 + self.a3 + 1))
        ax.axes.set_ylim3d(bottom=-self.a1 - 1, top=self.a1 + 1)
        ax.axes.set_zlim3d(bottom=-self.a1 - 1, top=self.a1 + 1)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.plot3D(np.array([self.origin[0][0], self.link_1_origin[0][0]]),
                  np.array([self.origin[1][0], self.link_1_origin[1][0]]),
                  np.array([self.origin[2][0], self.link_1_origin[2][0]]),
                  marker="o")
        ax.plot3D(np.array([self.link_1_origin[0][0], self.link_2_origin[0][0]]),
                  np.array([self.link_1_origin[1][0], self.link_2_origin[1][0]]),
                  np.array([self.link_1_origin[2][0], self.link_2_origin[2][0]]),
                  marker="o")
        ax.plot3D(np.array([self.link_2_origin[0][0], self.link_3_origin[0][0]]),
                  np.array([self.link_2_origin[1][0], self.link_3_origin[1][0]]),
                  np.array([self.link_2_origin[2][0], self.link_3_origin[2][0]]),
                  marker="o")
        ax.plot3D(np.array([self.link_3_origin[0][0], self.extender_origin[0][0]]),
                  np.array([self.link_3_origin[1][0], self.extender_origin[1][0]]),
                  np.array([self.link_3_origin[2][0], self.extender_origin[2][0]]),
                  marker="o",
                  c='gray')
        ax.plot3D(np.array([self.extender_origin[0][0], self.effector_origin[0][0]]),
                  np.array([self.extender_origin[1][0], self.effector_origin[1][0]]),
                  np.array([self.extender_origin[2][0], self.effector_origin[2][0]]),
                  c='black',
                  marker="o")

        if axes:
            ax.quiver(self.x_axis_starts, self.y_axis_starts, self.z_axis_starts,
                      self.x_axis_x_ends, self.x_axis_y_ends, self.x_axis_z_ends,
                      normalize=True, color='red', length=axes_length)
            ax.quiver(self.x_axis_starts, self.y_axis_starts, self.z_axis_starts,
                      self.y_axis_x_ends, self.y_axis_y_ends, self.y_axis_z_ends,
                      normalize=True, color='green', length=axes_length)
            ax.quiver(self.x_axis_starts, self.y_axis_starts, self.z_axis_starts,
                      self.z_axis_x_ends, self.z_axis_y_ends, self.z_axis_z_ends,
                      normalize=True, color='blue', length=axes_length)

        plt.show()


class Spherical:
    def __init__(self, link_lengths=[1.0, 1.0, 1.0], effector_length=1.0, rotation_angles=[0.0, 0.0]):
        # Frame 0 origin
        self.origin = np.array([[0], [0], [0]])
        # Link lengths
        self.a1 = link_lengths[0]
        self.a2 = link_lengths[1]
        self.a3 = link_lengths[2]
        # End effector length
        self.effector_length = effector_length
        # Joint rotations
        self.theta_1 = rotation_angles[0]
        self.theta_2 = rotation_angles[1]
        # Orientation matrices frame to frame
        self.o_1_0 = create_orientation_matrix(['x', 'y', 'z'])
        self.o_2_1 = create_orientation_matrix(['x', 'z', '-y'])
        self.o_3_2 = create_orientation_matrix(['x', 'y', 'z'])
        # Displacement vectors frame to frame
        self.d_1_0 = create_displacement_vector([0, 0, self.a1])
        self.d_2_1 = create_displacement_vector([self.a2, 0, 0])
        self.d_3_2 = create_displacement_vector([self.a3, 0, 0])
        # Joint rotation matrices
        self.r_1 = create_rotation_matrix('z', rotation_angles[0])
        self.r_2 = create_rotation_matrix('z', rotation_angles[1])
        # Link vectors relative to their original frames
        self.link_1 = np.array([[0], [0], [self.a1], [1]])
        self.link_2 = np.array([[self.a2], [0], [0], [1]])
        self.link_3 = np.array([[self.a3], [0], [0], [1]])
        self.effector = np.array([[self.effector_length], [0], [0], [1]])
        # HTMs frame to frame
        self.htm_1_0 = create_htm(self.o_1_0, self.d_1_0, self.r_1)
        self.htm_2_1 = create_htm(self.o_2_1, self.d_2_1, self.r_2)
        self.htm_3_2 = create_htm(self.o_3_2, self.d_3_2)
        # HTMs to Frame 0
        self.htm_2_0 = create_origin_htm([self.htm_1_0, self.htm_2_1])
        self.htm_3_0 = create_origin_htm([self.htm_2_0, self.htm_3_2])
        # Links in Frame 0
        self.link_1_origin = self.link_1
        self.link_2_origin = self.htm_1_0 @ self.link_2
        self.link_3_origin = self.htm_2_0 @ self.link_3
        # Final point of end effector in Frame 0
        self.effector_origin = self.htm_3_0 @ self.effector

        # Axes in origin frame
        self.general_x_axis = np.array([[1], [0], [0], [1]])
        self.general_y_axis = np.array([[0], [1], [0], [1]])
        self.general_z_axis = np.array([[0], [0], [1], [1]])
        self.general_origin = np.array([[0], [0], [0], [1]])
        self.f_0_origin = self.general_origin
        self.f_0_x = self.general_x_axis
        self.f_0_y = self.general_y_axis
        self.f_0_z = self.general_z_axis
        self.f_1_origin = self.htm_1_0 @ self.general_origin
        self.f_1_x = np.subtract(self.htm_1_0 @ self.general_x_axis, self.f_1_origin)
        self.f_1_y = np.subtract(self.htm_1_0 @ self.general_y_axis, self.f_1_origin)
        self.f_1_z = np.subtract(self.htm_1_0 @ self.general_z_axis, self.f_1_origin)
        self.f_2_origin = self.htm_2_0 @ self.general_origin
        self.f_2_x = np.subtract(self.htm_2_0 @ self.general_x_axis, self.f_2_origin)
        self.f_2_y = np.subtract(self.htm_2_0 @ self.general_y_axis, self.f_2_origin)
        self.f_2_z = np.subtract(self.htm_2_0 @ self.general_z_axis, self.f_2_origin)
        self.f_3_origin = self.htm_3_0 @ self.general_origin
        self.f_3_x = np.subtract(self.htm_3_0 @ self.general_x_axis, self.f_3_origin)
        self.f_3_y = np.subtract(self.htm_3_0 @ self.general_y_axis, self.f_3_origin)
        self.f_3_z = np.subtract(self.htm_3_0 @ self.general_z_axis, self.f_3_origin)

        self.x_axis_starts = [self.f_0_origin[0][0], self.f_1_origin[0][0], self.f_2_origin[0][0],
                              self.f_3_origin[0][0]]
        self.y_axis_starts = [self.f_0_origin[1][0], self.f_1_origin[1][0], self.f_2_origin[1][0],
                              self.f_3_origin[1][0]]
        self.z_axis_starts = [self.f_0_origin[2][0], self.f_1_origin[2][0], self.f_2_origin[2][0],
                              self.f_3_origin[2][0]]

        self.x_axis_x_ends = [self.f_0_x[0][0], self.f_1_x[0][0], self.f_2_x[0][0], self.f_3_x[0][0]]
        self.x_axis_y_ends = [self.f_0_x[1][0], self.f_1_x[1][0], self.f_2_x[1][0], self.f_3_x[1][0]]
        self.x_axis_z_ends = [self.f_0_x[2][0], self.f_1_x[2][0], self.f_2_x[2][0], self.f_3_x[2][0]]

        self.y_axis_x_ends = [self.f_0_y[0][0], self.f_1_y[0][0], self.f_2_y[0][0], self.f_3_y[0][0]]
        self.y_axis_y_ends = [self.f_0_y[1][0], self.f_1_y[1][0], self.f_2_y[1][0], self.f_3_y[1][0]]
        self.y_axis_z_ends = [self.f_0_y[2][0], self.f_1_y[2][0], self.f_2_y[2][0], self.f_3_y[2][0]]

        self.z_axis_x_ends = [self.f_0_z[0][0], self.f_1_z[0][0], self.f_2_z[0][0], self.f_3_z[0][0]]
        self.z_axis_y_ends = [self.f_0_z[1][0], self.f_1_z[1][0], self.f_2_z[1][0], self.f_3_z[1][0]]
        self.z_axis_z_ends = [self.f_0_z[2][0], self.f_1_z[2][0], self.f_2_z[2][0], self.f_3_z[2][0]]

    # Finds xyx coordinates of end effector given theta 1 and 2 in radians
    def find_xyz(self, theta_1, theta_2):
        x = (self.a2 + self.a3 * np.cos(theta_2)) * np.cos(theta_1)
        y = (self.a2 + self.a3 * np.cos(theta_2)) * np.sin(theta_1)
        z = self.a1 + self.a3 * np.sin(theta_2)
        return np.array([x, y, z])

    def plot(self, figure_name="Spherical Plot", axes=False, axes_length=1):
        # Plot the location of robot with current configuration
        plt.figure(figure_name)
        ax = plt.axes(projection='3d')
        ax.axes.set_xlim3d(left=-(self.a2 + self.a3 + 1), right=(self.a2 + self.a3 + 1))
        ax.axes.set_ylim3d(bottom=-self.a1 - 1, top=self.a1 + 1)
        ax.axes.set_zlim3d(bottom=-self.a1 - 1, top=self.a1 + 1)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.plot3D(np.array([self.origin[0][0], self.link_1_origin[0][0]]),
                  np.array([self.origin[1][0], self.link_1_origin[1][0]]),
                  np.array([self.origin[2][0], self.link_1_origin[2][0]]),
                  marker="o")
        ax.plot3D(np.array([self.link_1_origin[0][0], self.link_2_origin[0][0]]),
                  np.array([self.link_1_origin[1][0], self.link_2_origin[1][0]]),
                  np.array([self.link_1_origin[2][0], self.link_2_origin[2][0]]),
                  marker="o")
        ax.plot3D(np.array([self.link_2_origin[0][0], self.link_3_origin[0][0]]),
                  np.array([self.link_2_origin[1][0], self.link_3_origin[1][0]]),
                  np.array([self.link_2_origin[2][0], self.link_3_origin[2][0]]),
                  marker="o")
        ax.plot3D(np.array([self.link_3_origin[0][0], self.effector_origin[0][0]]),
                  np.array([self.link_3_origin[1][0], self.effector_origin[1][0]]),
                  np.array([self.link_3_origin[2][0], self.effector_origin[2][0]]),
                  marker="o",
                  c='gray')

        if axes:
            ax.quiver(self.x_axis_starts, self.y_axis_starts, self.z_axis_starts,
                      self.x_axis_x_ends, self.x_axis_y_ends, self.x_axis_z_ends,
                      normalize=True, color='red', length=axes_length)
            ax.quiver(self.x_axis_starts, self.y_axis_starts, self.z_axis_starts,
                      self.y_axis_x_ends, self.y_axis_y_ends, self.y_axis_z_ends,
                      normalize=True, color='green', length=axes_length)
            ax.quiver(self.x_axis_starts, self.y_axis_starts, self.z_axis_starts,
                      self.z_axis_x_ends, self.z_axis_y_ends, self.z_axis_z_ends,
                      normalize=True, color='blue', length=axes_length)

        plt.show()

    def find_angles(self, coordinates=[2, 0, 1], print_info=False):
        coordinates = np.array(coordinates).astype(float)
        theta_2 = np.arcsin((coordinates[2] - self.a1) / self.a3)
        theta_1 = np.arcsin(coordinates[1] / (self.a2 + self.a3 * np.cos(theta_2)))
        xyz = self.find_xyz(theta_1, theta_2)

        is_valid = np.all(coordinates == xyz)

        if print_info:
            if is_valid:
                print(f'For coordinates {coordinates} theta_1 and theta_2 are ({np.round(np.rad2deg(theta_1), 2)},'
                      f'{np.round(np.rad2deg(theta_2), 2)}) degrees')
            else:
                print(f'The given coordinates {coordinates} are not in the workspace given the current parameters.')

        if is_valid:
            return np.rad2deg(theta_1), np.rad2deg(theta_2)
        else:
            return None, None

    def plot_workspace(self, figure_name="Spherical workspace"):
        theta_1 = np.deg2rad(np.linspace(0, 360, 30))
        theta_2 = theta_1
        theta_1, theta_2 = np.meshgrid(theta_1, theta_2)
        [xs, ys, zs] = self.find_xyz(theta_1, theta_2)

        # Plot the location of robot with current configuration
        plt.figure(figure_name)
        ax = plt.axes(projection='3d')
        ax.axes.set_xlim3d(left=-(self.a2 + self.a3 + 1), right=(self.a2 + self.a3 + 1))
        ax.axes.set_ylim3d(bottom=-(self.a2 + self.a3 + 1), top=(self.a2 + self.a3 + 1))
        ax.axes.set_zlim3d(bottom=-self.a1 - 1, top=self.a1 + 1)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.plot_surface(xs, ys, zs, cmap=cm.coolwarm)

        plt.show()

    def update(self, link_lengths=None, effector_length=None, rotation_angles=None):
        if not link_lengths:
            a1 = self.a1
            a2 = self.a2
            a3 = self.a3
        else:
            a1 = link_lengths[0]
            a2 = link_lengths[1]
            a3 = link_lengths[2]
        if not effector_length:
            effector_length = self.effector_length
        if not rotation_angles:
            theta_1 = self.theta_1
            theta_2 = self.theta_2

        self.__init__(link_lengths=[a1, a2, a3], effector_length=effector_length, rotation_angles=[theta_1, theta_2])


if __name__ == '__main__':

    # scara = Scara(end_effector_displacement=.5, rotation_angles=[10, 10, 10], effector_length=.25)
    # scara.plot(axes=True, axes_length=.2)
    spherical = Spherical(link_lengths=[1, 1, 1], effector_length=.5, rotation_angles=[45, 135])
    # spherical.plot(axes=True, axes_length=.2)
    pprint(spherical.find_angles(coordinates=[1, 1, 1], print_info=True))
    spherical.plot_workspace()