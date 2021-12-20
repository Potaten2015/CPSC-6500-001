"""
Week 7 Assignment: Solve Prismatic Manipulator
Author: Taten H. Knight
Date: 2021.12.19

Notes:
    - I assumed that the goal was to calculate the joint variable values given a certain x,y,z position. This
    assignment seemed very simple to me but I may have misinterpreted the directions.
"""


def solve(x, y, z, a1=1, a2=2, a3=3):
    d1 = z - a1
    d2 = x - a2
    d3 = -y -a3
    print(f'd1 = {d1}')
    print(f'd2 = {d2}')
    print(f'd3 = {d2}')


def run():
    solve(3, 3, 3)


if __name__ == '__main__':
    run()