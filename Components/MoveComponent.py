#!/usr/bin/python
#-*-coding:utf-8-*-

from Component import Component

class MoveComponent(Component):
    '''This is the moveable component.'''
    _name = 'MoveComponent'

    def move(self,cmd):
        '''Input L,R,U,D  or S to move the component or stop. Rise exception if moving out of region.'''
        cmd = cmd.upper()
        if cmd == 'L':
            if self.position[0]-1 >= 0:
                self.position = (self.position[0]-1,self.position[1])
            else:
                raise MoveOutOfRegion(self,cmd)
        elif cmd == 'R':
            if self.position[0]+1 < self._region_size[0]:
                self.position = (self.position[0]+1,self.position[1])
            else:
                raise MoveOutOfRegion(self,cmd)
        elif cmd == 'U':
            if self.position[1]-1 >= 0:
                self.position = (self.position[0],self.position[1]-1)
            else:
                raise MoveOutOfRegion(self,cmd)
        elif cmd == 'D':
            if self.position[1]+1 < self._region_size[1]:
                self.position = (self.position[0],self.position[1]+1)
            else:
                raise MoveOutOfRegion(self,cmd)
        elif cmd == 'S':
            pass

    def moveable_direction(self):
        direction = ['S']
        if self.position[0] > 0:
            direction.append('L')
        if self.position[0] < self._region_size[0]-1:
            direction.append('R')
        if self.position[1] > 0:
            direction.append('U')
        if self.position[1] < self._region_size[1]-1:
            direction.append('D')
        return direction
