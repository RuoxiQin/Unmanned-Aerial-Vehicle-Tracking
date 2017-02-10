#!/usr/bin/python
#-*-coding:utf-8-*-
def display_region(region):
    '''This function print the region in the right way'''
    x_length = len(region)
    y_length = len(region[0])
    dis = [[0 for x in range(y_length)] for y in range(x_length)]
    for y in range(y_length):
        for x in range(x_length):
            dis[x][y] = region[y][x]
    for line in dis:
        for x in line:
            print '%.5f\t' % x,
        print '\n',
    print '\n',
