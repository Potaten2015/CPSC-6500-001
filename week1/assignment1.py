import numpy as np
from pprint import pprint

# question 1
a = np.array([5, 6, 1, 3, 8, 9, 2])

sum = a.sum()
average = a.mean()
max = a.max()
min = a.min()

print('sum: ', sum)
print('average: ', average)
print('max: ', max)
print('min: ', min)

# question 2
A = [
    [1, 0, 2],
    [2, 1, 0.5],
    [0, 0, 2]
]

B = [
    [3, 1, 0],
    [0, 2, 0.5],
    [0, 0.2, 1]
]

sum = np.add(np.multiply(A, 3), B)
pprint(sum)

# question 3
# np.random.rand returns random number [0, 1)
# if we multiply this by -6 we get (-6, 0]
# and add 3 we get (-3, 3]
random_array = np.add(np.multiply(np.random.rand(3, 3, 3), -6), 3)
pprint(random_array)

# question 4
def my_norm(mat):
    sum_of_squares = np.sum(np.multiply(mat, mat))
    norm = np.sqrt(sum_of_squares)
    return norm

a = np.array([-1, 2, -3, 4, -5])
print('my norm: ', my_norm(a))
print('numpy norm: ', np.linalg.norm(a))