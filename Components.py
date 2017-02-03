'''This packge contains the components of the testplatform'''
from UAV_exception import PlaneLowPower, MoveOutOfRegion,IntruderExposed

#仿真平台里的各个元件
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

class Base(Component):
    '''This is the base.'''
    _name = 'Base'
    
    def charge(self,planes):
        '''charge the planes. need to input the list of planes.'''
        for plane in planes:
            if plane.position == self.position:
                plane.get_charged()
                
class Plane(MoveComponent):
    '''This is the plane.'''
    _name = 'Plane'

    def __init__(self,position,num,region_size,max_battery=20, plane_sight = 1, battery = None):
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



        
        
        
if __name__ == '__main__':
    p = Plane((7,0),0,(8,8))
    b = Base((3,4),0,(8,8))
    i = Intruder((3,5),0,(8,8))
    planes = [p]
    intruders = [i]

    print p.moveable_direction()





