#!/usr/bin/python
#-*-coding:utf-8-*-

'''This packge contains the algorithem of the UAV searching.
    The algorithem must conform to the standard OperateInterface defined
    in the PlatForm class.'''

from test_tools.OperateInterface import OperateInterface
from test_tools.tools import *
import math
from Components.Base import Base
from Components.Plane import Plane
from Components.Intruder import Intruder
import random

#实际上没用这个库

class MannulControl(OperateInterface):
    '''This is a mannul control algorithem.'''
    def initiate(self,planes,bases,region_size,max_plane_battery,intruder_exposed_time, plane_sight, max_semo_intruder, target_move):
        print 'The size of the patrol region is %d * %d' % (region_size[0], region_size[1])
        print 'There are ', len(planes), 'planes, which are:'
        for plane in planes:
            print plane
        print 'Now you are in control! Please make your move, good luck!'

    def decide(self,plane, planes, bases):
        if plane.find_intruder:
            print 'Find an intruder at ', plane.intruder_position
        else:
            print 'Everything is allright.'
        print 'Input the command of ', plane, '. Battery ',plane.battery,' : '
        return raw_input()

class SemiautoControl(MannulControl):
    def initiate(self,planes,bases,region_size,max_plane_battery,intruder_exposed_time, plane_sight, max_semo_intruder, target_move):
        self.cmd_list = ['D','D','R','R','U','U','L','L']
        self.pointer = 0
        return super(SemiautoControl,self).initiate(planes,bases,region_size,max_plane_battery,intruder_exposed_time)

    def decide(self, plane, planes, intruders):
        if plane.find_intruder:
            pass#print 'Find an intruder at ', plane.intruder_position
        else:
            pass#print 'Everything is allright.'

        cmd = self.cmd_list[self.pointer]
        self.pointer += 1
        if self.pointer >= len(self.cmd_list):
            self.pointer = 0

        #print 'Input the command of ', plane, '. Battery ',plane.battery,' : ', cmd
        return cmd

class DirectControl_v1_0(OperateInterface):
    '''This is the first vision of the tracing algorithem.'''
    pass

class DirectControl_v1_0Controller(object):
    '''This is the single plane controller using in the DirectControl_v1_0'''
    def __init__(self, plane, base, patrol_list, max_hunt_heat, max_battery, max_exposed_time):
        self.state_list = {'patrol': self.patrol, 'go_to': self.go_to, 'follow': self.follow, 'charge': self.charge}
        self.plane = plane
        self.base = base
        self.patrol_list = patrol_list[:]
        self.patrol_pointer = 0
        self.max_hunt_heat = max_hunt_heat
        self.hunt_heat = 0
        self.max_battery = max_battery
        self.intruder_num = None
        self.exposed_time = 0

        self.stack = [0, 'patrol' ]
        self.state = 'go_to'
        self.go_to_destination = patrol_list[0]
        return super(DirectControl_v1_0Controller, self).__init__()

    def next(self):
        '''Call this method to get the next command.'''
        return self.state_list[self.state]()

    def patrol(self):
        def save_patrol():
            self.stack.append(self.patrol_pointer)
            self.stack.append('patrol')

        if self.low_power():
            save_patrol()
            return self.charge()
        elif self.plane.find_intruder:
            save_patrol()
            self.suspect_position = self.plane.intruder_position
            return self.follow()
        else:
            if self.plane.position == self.patrol_list[self.patrol_pointer]:
                self.patrol_pointer += 1
                if self.patrol_pointer >= len(self.state_list):
                    self.patrol_pointer = 0
            return direct(self.plane.position, self.patrol_list[self.patrol_pointer])

    def go_to(self):
        def save_go_to():
            self.stack.append(self.go_to_destination)
            self.stack.append('go_to')

        if self.low_power():
            save_go_to()
            return self.charge()
        elif self.plane.find_intruder:
            save_go_to()
            self.suspect_position = self.plane.intruder_position
            return self.follow()
        else:
            if self.plane.position != self.go_to_destination:
                return direct(self.plane.position, self.go_to_destination)
            else:
                return self.state_transfer()

    def follow(self):
        def save_follow():
            self.stack.append(self.exposed_time)
            self.stack.append(self.intruder_num)
            self.stack.append(self.hunt_heat)
            self.stack.append('follow')

        if self.low_power():
            save_follow()
            return self.charge()
        else:
            if self.plane.find_intruder:
                self.hunt_heat = self.max_hunt_heat
                if self.plane.intruder_num == self.intruder_num:
                    self.exposed_time += 1
                    if self.exposed_time >= self.max_exposed_time:
                        self.exposed_time = 0
                        return self.state_transfer()
                    else:
                        return direct(self.plane.position, self.suspect_position)
                else:
                    self.intruder_num = self.plane.intruder_num
                    self.exposed_time = 1
                    return direct(self.plane.position, self.suspect_position)
            else:
                if self.hunt_heat > 0:
                    self.hunt_heat -= 1
                    return direct(self.plane.position, self.suspect_position)
                else:
                    self.hunt_heat = 0
                    return self.state_transfer()

    def charge(self):
        if self.plane.position != self.base.position:
            return direct(self.plane.position, self.base.position)
        else:
            return self.state_transfer()

    def state_transfer(self):
        cmd = self.stack.pop()
        if cmd == 'patrol':
            self.patrol_pointer = self.stack.pop()
        elif cmd == 'go_to':
            self.go_to_destination = self.stack.pop()
        elif cmd == 'follow':
            self.hunt_heat = self.stack.pop()
            self.intruder_num = self.stack.pop()
            self.exposed_time = self.stack.pop()

        self.state = cmd
        return self.next()

    def low_power(self):
        return self.plane.battery <= distance(self.plane.position,self.base.position) + 2




class DirectControl_v1_1(OperateInterface):
    def __init__(self, max_hunt_heat):
        self.__max_hunt_heat = max_hunt_heat
        return super(DirectControl_v1_1, self).__init__()

    def initiate(self,planes,bases,region_size,max_plane_battery,intruder_exposed_time, plane_sight, max_semo_intruder, target_move):
        #trace planing
        zoom_num = math.ceil(region_size[0] / float(1 + 2 * plane_sight))
        ceil_whole_distance = zoom_num*(region_size[1]-2*plane_sight) + (zoom_num-1)*(2*plane_sight)
        each_plane_distance = math.ceil(ceil_whole_distance /
                                        float(len(planes))) + 2
        patrol_list = []
        is_odd = True
        #calculate the coordinate of the patrol line
        for x in range(plane_sight,region_size[0],2*plane_sight + 1):
            if is_odd:
                patrol_list.append((x,plane_sight))
                patrol_list.append((x,region_size[1]-1-plane_sight))
            else:
                patrol_list.append((x,region_size[1]-1-plane_sight))
                patrol_list.append((x,plane_sight))
            is_odd = not is_odd
        if region_size[0]-1 > patrol_list[-1][0] + plane_sight:
            if is_odd:
                patrol_list.append((region_size[0]-1,plane_sight))
                patrol_list.append((region_size[0]-1,region_size[1]-1-plane_sight))
            else:
                patrol_list.append((region_size[0]-1,region_size[1]-1-plane_sight))
                patrol_list.append((region_size[0]-1,plane_sight))

        #go through the whole patrol line and identified the patrol list of each plane
        class trace_designeer(Components.MoveComponent):
            def __init__(self, position):
                self.pace_counter = 0
                return super(trace_designeer, self).__init__(position, 0, region_size)

            def move(self, cmd):
                self.pace_counter += 1
                return super(trace_designeer, self).move(cmd)
        #The patrol list do not have duplicated objects
        class PatrolList(list):
            def append(self, obj):
                if len(self) == 0 or self[-1] != obj:
                    super(PatrolList, self).append(obj)

        tracer = trace_designeer(patrol_list[0])
        all_patrol_list = []
        plane_index = 1
        one_patrol_list = PatrolList()
        for destination in patrol_list:
            while tracer.position != destination:
                tracer.move(direct(tracer.position, destination))
                if tracer.pace_counter >= plane_index * each_plane_distance:
                    one_patrol_list.append(tracer.position)
                    all_patrol_list.append(one_patrol_list[:])
                    one_patrol_list = PatrolList()
                    one_patrol_list.append(tracer.position)
                    plane_index += 1
            one_patrol_list.append(destination)
        all_patrol_list.append(one_patrol_list[:])

        #identified the charge bases of each plane
        nearest_bases = []
        for trace in all_patrol_list:
            nearest_base = bases[0]
            for base in bases:
                if distance(trace[0], base.position) < distance(trace[0], nearest_base.position):
                    nearest_base = base
            nearest_bases.append(nearest_base)

        #MainController initialization and others
        self.main_controllers = []
        for index in range(len(planes)):
            self.main_controllers.append(DirectControl_v1_1MainController(planes[index],
                                                                     nearest_bases[index], all_patrol_list[index],
                                                                     self.__max_hunt_heat, max_plane_battery,
                                                                     intruder_exposed_time))
            print self.main_controllers[index]

    def decide(self, plane, planes, bases):
        for controller in self.main_controllers:
            if controller.plane == plane:
                cmd = controller.next()
                #print plane, 'Move: ', cmd
                return cmd

class DirectControl_v1_1MainController(object):
    '''This is the tracing algorithem DirectControl v1.1.'''
    def __init__(self, plane, base, patrol_list, max_hunt_heat, max_battery, max_exposed_time):
        self.plane = plane
        self.patrol = DirectControl_v1_1PatrolController(self,patrol_list)
        self.goto = DirectControl_v1_1GoToController(self,patrol_list[0])
        self.follow = DirectControl_v1_1FollowController(self,max_hunt_heat, max_exposed_time)
        self.charge = DirectControl_v1_1ChargeController(self, base, max_battery)
        self.state_list = {'patrol': self.patrol, 'goto': self.goto, 'follow': self.follow, 'charge': self.charge}

        self.stack = [0, 'patrol' ]
        self.state = 'goto'
        return super(DirectControl_v1_1MainController, self).__init__()

    def test_low_power(self):
        if self.plane.battery <= distance(self.plane.position,self.charge.base.position) + 2 and\
                self.state != 'charge':
            self.state_list[self.state].save()
            self.state = 'charge'

    def test_find_intruder(self) :
        if self.plane.find_intruder and self.state != 'charge' and self.state != 'follow':
            self.state_list[self.state].save()
            self.state = 'follow'

    def next(self):
        self.test_low_power()
        self.test_find_intruder()  
        return self.state_list[self.state].get_cmd()

    def state_transfer(self):
        self.state = self.stack.pop()
        self.state_list[self.state].get_stack_init()
        return self.state_list[self.state].get_cmd()

    def __str__(self):
        return 'Plane: ' + str(self.plane) +'\nCharging base: ' + str(self.charge.base) + '\nPatrol list: ' + str(self.patrol.patrol_list)

class DirectControl_v1_1SubController(object):
    def __init__(self, main_controller):
        self.main_controller = main_controller
        return super(DirectControl_v1_1SubController, self).__init__()

    def __str__(self):
        assert 0, 'DirectControl_v1_1SubController. Must specific one sub controller!'

    def get_cmd(self):
        assert 0, 'Must specific one sub controller!'

    def save(self):
        assert 0, 'Must specific one sub controller!'

    def get_stack_init(self):
        assert 0, 'Must specific one sub controller!'

class DirectControl_v1_1PatrolController(DirectControl_v1_1SubController):
    def __init__(self, main_controller, patrol_list):
        self.patrol_list = patrol_list[:]
        self.pointer = 0
        return super(DirectControl_v1_1PatrolController, self).__init__(main_controller)

    def __str__(self):
        return 'patrol'

    def save(self):
        self.main_controller.stack.append(self.pointer)
        self.main_controller.stack.append('patrol')    

    def get_cmd(self):
        if self.main_controller.plane.position == self.patrol_list[self.pointer]:
                self.pointer += 1
                if self.pointer >= len(self.patrol_list):
                    self.pointer = 0
        return direct(self.main_controller.plane.position, self.patrol_list[self.pointer])

    def get_stack_init(self):
        self.pointer = self.main_controller.stack.pop()

class DirectControl_v1_1GoToController(DirectControl_v1_1SubController):
    def __init__(self, main_controller, first_destination):
        self.destination = first_destination
        return super(DirectControl_v1_1GoToController, self).__init__(main_controller)

    def __str__(self):
        return 'goto'

    def save(self):
        self.main_controller.stack.append(self.destination)
        self.main_controller.stack.append('goto')

    def get_stack_init(self):
        self.destination = self.main_controller.stack.pop()

    def get_cmd(self):
        if self.main_controller.plane.position != self.destination:
             return direct(self.main_controller.plane.position, self.destination)
        else:
             return self.main_controller.state_transfer()

class DirectControl_v1_1FollowController(DirectControl_v1_1SubController):
    def __init__(self, main_controller, max_hunt_heat, max_exposed_time):
        self.max_hunt_heat = max_hunt_heat
        self.hunt_heat = 0
        self.intruder_num = None
        self.exposed_time = 0   
        self.max_exposed_time = max_exposed_time
        return super(DirectControl_v1_1FollowController, self).__init__(main_controller)

    def __str__(self):
        return 'follow'

    def save(self):
        self.main_controller.stack.append(self.exposed_time)
        self.main_controller.stack.append(self.intruder_num)
        self.main_controller.stack.append(self.hunt_heat)
        self.main_controller.stack.append('follow')

    def get_stack_init(self):
        self.hunt_heat = self.main_controller.stack.pop()
        self.intruder_num = self.main_controller.stack.pop()
        self.exposed_time = self.main_controller.stack.pop()

    def get_cmd(self):
        #print 'Find intruder, hunt heat: ', self.hunt_heat
        if self.main_controller.plane.find_intruder:
            self.hunt_heat = self.max_hunt_heat
            self.suspect_position = self.main_controller.plane.intruder_position
            #print  '\tSuspect position ' , self.suspect_position
            if self.main_controller.plane.intruder_num == self.intruder_num:
                self.exposed_time += 1
                if self.exposed_time >= self.max_exposed_time:
                    self.exposed_time = 0
                    return self.main_controller.state_transfer()
                else:
                    return direct(self.main_controller.plane.position, self.suspect_position)
            else:
                self.intruder_num = self.main_controller.plane.intruder_num
                self.exposed_time = 1
                return direct(self.main_controller.plane.position, self.suspect_position)
        else:
            if self.hunt_heat > 0:
                self.hunt_heat -= 1
                return direct(self.main_controller.plane.position, self.suspect_position)
            else:
                self.hunt_heat = 0
                return self.main_controller.state_transfer()

class DirectControl_v1_1ChargeController(DirectControl_v1_1SubController):
    def __init__(self, main_controller, base, max_battery):
        self.base = base
        self.max_battery = max_battery
        return super(DirectControl_v1_1ChargeController, self).__init__(main_controller)

    def __str__(self):
        return 'charge'

    def save(self):
        assert 0, 'Charge sub controller do not need to save!'

    def get_stack_init(self):
        assert 0, 'Charge sub controller do not have stack state!'

    def get_cmd(self):
        if self.main_controller.plane.position != self.base.position:
            return direct(self.main_controller.plane.position, self.base.position)
        else:
            return self.main_controller.state_transfer()

class RandomControl(OperateInterface):
    '''This is a random control algorithem.'''
    def __init__(self, display_cmd = False):
        self.display_cmd = display_cmd
        return super(RandomControl, self).__init__()

    def initiate(self,planes,bases,region_size,max_plane_battery,intruder_exposed_time, plane_sight, max_semo_intruder, target_move):
        if self.display_cmd:
            print 'The size of the patrol region is %d * %d' % (region_size[0], region_size[1])
            print 'There are ', len(planes), 'planes, which are:'
            for plane in planes:
                print plane
            print 'There are ', len(bases), 'bases, which are:'
            for base in bases:
                print base
            print 'Now start random control!'

    def decide(self,plane, planes, bases, found_intruders_position):
        cmd = random.choice(plane.moveable_direction())
        if self.display_cmd:
            if plane.find_intruder:
                print plane, 'find an intruder at ', plane.intruder_position
            else:
                print plane, 'don\'t see intruder.'
            print 'We move the ', plane, 'to', cmd,'.\n'
        return cmd


if __name__ == '__main__':
    import Components
    import UAV_exception
    intruder_exposed_time = 9
    plane_battery = 100
    region_size = (13,9)
    base_position1 = (0,0)
    base_position2 = (8,0)
    p1 = Components.Plane(base_position1,0,region_size,plane_battery)
    p2 = Components.Plane(base_position2,1,region_size,plane_battery)
    b1 = Components.Base(base_position1,0,region_size)
    b2 = Components.Base(base_position2,1,region_size)
    Ps = [p1, p2]
    Bs = [b1, b2]

    test = DirectControl_v1_1()
    test.initiate(Ps,Bs, region_size, plane_battery, 5, 1)

