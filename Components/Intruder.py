#!/usr/bin/python
#-*-coding:utf-8-*-

from MoveComponent import MoveComponent

class Intruder(MoveComponent):
    '''This is the class of intruder.'''
    _name = 'Intruder'

    def __init__(self,position,num,region_size,max_exposed_time=3):
        self.__exposed_time = 0
        self.__live_time = 0
        self.__max_exposed_time = max_exposed_time
        super(Intruder,self).__init__(position,num,region_size)

    def add_exposed_time(self):
        self.__exposed_time += 1
        if self.__exposed_time >= self.__max_exposed_time:
            raise IntruderExposed(self)

    def add_live_time(self):
        self.__live_time += 1

    def get_live_time(self):
        return self.__live_time
