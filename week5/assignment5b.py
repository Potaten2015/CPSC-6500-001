"""
Author: Taten H. Knight
Creation Date:  2021.12.05
Title: Assignment 5b
Topic: Denavit-Hartenberg Matrix
Description: Function for creating DHT, HTMS, and end-effector final position
"""


import numpy as np
from pprint import pprint


def htm_from_hartenberg(rows):
    htms = []
    for row in rows:
        theta = np.deg2rad(row[0])
        alpha = np.deg2rad(row[1])
        htm = np.array([
            [np.cos(theta), -np.sin(theta) * np.cos(theta), np.sin(theta) * np.sin(alpha), row[2] * np.cos(theta)],
            [np.sin(theta), np.cos(theta) * np.cos(alpha), -np.cos(theta) * np.sin(alpha), row[2] * np.sin(theta)],
            [0, np.sin(alpha), np.cos(alpha), row[3]],
            [0, 0, 0, 1]
        ])
        htms.append(htm)
    return htms


def hartenberg_table(lengths=[1, 1, 1], angle=0):
    hartenberg_rows = np.array([
        [angle, 0, lengths[1], lengths[0]],
        [0, 0, 0, lengths[2]]
    ])
    return hartenberg_rows


def end_effector_position(htms, starting_position):
    final_position = np.identity(4)
    for htm in htms:
        final_position = final_position @ htm
    final_position = final_position @ starting_position
    return final_position


def run():
    hartenberg = hartenberg_table(angle=180)
    htms = htm_from_hartenberg(hartenberg)
    position = end_effector_position(htms, np.array([[0], [0], [0], [1]]))
    pprint(position[:3].round(2))


run()