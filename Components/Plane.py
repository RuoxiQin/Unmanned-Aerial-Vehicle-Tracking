#!/usr/bin/python
#-*-coding:utf-8-*-

from MoveComponent import MoveComponent
from UAV_exception import PlaneLowPower, MoveOutOfRegion,IntruderExposed

class Plane(MoveComponent):
    '''This is the plane.'''
    _name = 'Plane'

    def __init__(self,position,num,region_size,max_battery = 20, plane_sight = 1, battery = None):
        super(Plane,self).__init__(position,num,region_size)
        self.__max_battery = max_battery
        self.__plane_sight = plane_sight
        if battery == None:
            self.battery = max_battery
        else:
            self.battery = battery
        self.find_intruder = False

    def __eq__(self, other):
        return isinstance(other, Plane) and self.num == other.num

    def get_charged(self):
        self.battery = self.__max_battery

    def move(self,cmd):
        assert self.battery >= -3
        super(Plane,self).move(cmd)
        self.battery -= 1
        if self.battery <= 0:
            raise PlaneLowPower(self)

    def find_intruders(self,intruders):
        for intruder in intruders:
            if intruder.position[0] <= self.position[0] + self.__plane_sight and intruder.position[0] >= self.position[0] - self.__plane_sight and intruder.position[1] <= self.position[1] + self.__plane_sight and intruder.position[1] >= self.position[1] - self.__plane_sight:
                self.intruder_position = intruder.position
                self.find_intruder = True
                self.intruder_num = intruder.num
                intruder.add_exposed_time()
                break
        else:
            self.find_intruder = False

    def __str__(self):
        return super(Plane,self).__str__() + 'Battery:%d' % self.battery
