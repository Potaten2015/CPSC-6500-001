import numpy as np
import matplotlib.pyplot as plt
from pprint import pprint


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
        htm = rotation_matrix @ orientation_matrix
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

    def __init__(self, link_lengths=[1.0, 1.0, 1.0], effector_length=1.0, rotation_angles=[0.0, 0.0, 0.0], end_effector_displacement=0.0):
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

    def plot(self, figure_name="Scara Plot"):
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

        plt.show()


if __name__ == '__main__':
    scara = Scara(end_effector_displacement=.5, rotation_angles=[90, -45, 0], effector_length=.25)
    scara.plot()
