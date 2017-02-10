#!/usr/bin/python
#-*-coding:utf-8-*-
#仿真平台
#define multiprocess function

import random

def multi_process_decide(pipe):
    algo = pipe.recv()
    one_plane = pipe.recv()
    planes = pipe.recv()
    bases = pipe.recv()
    found_intruders_position = pipe.recv()
    #print one_plane, 'start to make decision.'
    cmd = algo.decide(one_plane, planes, bases, found_intruders_position)
    pipe.send(cmd)
def distance(position1, position2):
    '''This tool return the distence between position1 and position2.'''
    return abs(position1[0] - position2[0]) + abs(position1[1] - position2[1])

def shortest_way(start,destination):
    '''This tool return a list of command which leads the component the shortest way to their destination.'''
    cmd = []
    if destination[0] >= start[0]:
        for i in range(destination[0] - start[0]):
            cmd.append('R')
    else:
        for i in range(start[0] - destination[0]):
            cmd.append('L')

    if destination[1] >= start[1]:
        for i in range(destination[1] - start[1]):
            cmd.append('D')
    else:
        for i in range(start[1] - destination[1]):
            cmd.append('U')

    return cmd

def direct(start,destination):
    '''This tool return an command directing the component to the destination.'''
    direction = []
    hori = destination[0] - start[0]
    if hori >= 0:
        direction.append('R')
    else:
        direction.append('L')
    verti = destination[1] - start[1]
    if verti >= 0:
        direction.append('D')
    else:
        direction.append('U')

    if abs(hori) + abs(verti) == 0:
        return 'S'
    else:
        cmd = random.randint(1, abs(hori) + abs(verti))
        if cmd <= abs(hori):
            return direction[0]
        else:
            return direction[1]

def is_endangerous(bases, plane):
    '''This function test whether one plane is endangerous.if it is not, return the difference between distance and battery level.'''
    return (plane.battery <= distance(sorted(bases, key = lambda base:distance(base.position, plane.position))[0].position, plane.position))

def realetive_position(my_position, reference):
    '''This function return my reletive position of refrence. return LU, LD, RU, RD'''
    if my_position[0] <= reference[0]:
        position = "L"
    else:
        position = "R"
    if my_position[1] <= reference[1]:
        return position + "U"
    else:
        return position + "D"

def list_sum(list):
    '''return the sum of the elements in list.'''
    sum = 0
    for item in list:
        sum += item
    return sum
