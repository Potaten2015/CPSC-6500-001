import numpy as np
from pprint import pprint

delta = np.array([
    [0, -3, 0, 1],
    [3, 0, 0, -1],
    [0, 0, 0, 0],
    [0, 0, 0, 0]
])

T = np.array([
    [1, 0, 0, 4],
    [0, 1, 0, 3],
    [0, 0, 1, 0],
    [0, 0, 0, 1]
])

w = np.array([
    [1],
    [2],
    [0],
    [1]
])

v = delta @ T @ w

pprint(v)