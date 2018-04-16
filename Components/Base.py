#!/usr/bin/python
#-*-coding:utf-8-*-

from Component import Component

class Base(Component):
    '''This is the base.'''
    _name = 'Base'

    def charge(self,planes):
        '''charge the planes. need to input the list of planes.'''
        for plane in planes:
            if plane.position == self.position:
                plane.get_charged()
