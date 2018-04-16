#!/usr/bin/python
#-*-coding:utf-8-*-

class Component(object):
    '''This is the component in the game.'''
    _name = 'Component'
    def __init__(self,position,num,region_size):
        self.position = position
        self.num = num
        self._region_size = region_size
        return super(Component, self).__init__()
    def __str__(self):
        return str(self._name)+ str(self.num) + ' position' +str(self.position)
