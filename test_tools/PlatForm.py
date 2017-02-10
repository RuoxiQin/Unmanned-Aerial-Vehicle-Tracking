#!/usr/bin/python
#-*-coding:utf-8-*-

from ResultRecord import ResultRecord
from Components.Base import Base
from Components.Plane import Plane
from Components.Intruder import Intruder
from copy import deepcopy
import UAV_exception
import random
import math
from test_tools.tools import *
import multiprocessing as mul

class PlatForm(object):
    def __init__(self, region_size, base_position_list, plane_position_list ,
                 all_intruder_num, decide_algorithem, max_semo_intruder=1,
                 target_move=False ,max_plane_battery = 20, max_exposed_time=4,
                 plane_sight = 1, show_info = False, max_simulate_time = float("inf"),
                 store_result = False, file_name = 'SimulateResult.txt'):
        self.store_result = store_result
        self.show_info = show_info
        self.__region_size = region_size
        self.__all_intruder_num = all_intruder_num
        self.__target_move = target_move
        self.__max_semo_intruder = max_semo_intruder
        self.__max_plane_battery = max_plane_battery
        self.__decide_algorithem = decide_algorithem
        self.__max_exposed_time = max_exposed_time
        self.__next_base_num = 0
        self.__next_plane_num = 0
        self.__next_intruder_num = 0
        self.__plane_sight = plane_sight
        self.__test_record = ResultRecord(self.store_result, file_name)
        self.max_simulate_time = max_simulate_time
        self.bases = []
        self.planes = []
        self.intruders = []
        self.detail_file = 'detail_file'
        self.end_simulation = False
        for base_position in base_position_list:
            self.__add_base(base_position)
        for plane_position in plane_position_list:
            self.__add_plane(plane_position)
        return super(PlatForm, self).__init__()

    def __add_base(self,base_position):
        '''Add base to bases list.'''
        if isinstance(base_position, Base):
            self.bases.append(base_position)
        else:
            self.bases.append(Base(base_position, self.__next_base_num, self.__region_size))
        self.__next_base_num += 1
    def __add_plane(self,plane_position):
        '''Add plane to planes list.'''
        if isinstance(plane_position, Plane):
            self.planes.append(plane_position)
        else:
            self.planes.append(Plane(plane_position, self.__next_plane_num, self.__region_size, self.__max_plane_battery, self.__plane_sight))
        self.__next_plane_num += 1
    def __add_intruder(self,intruder_position,):
        '''Add intruder to intruders list.'''
        if isinstance(intruder_position, Intruder):
            self.intruders.append(intruder_position)
        else:
            assert isinstance(intruder_position, tuple)
            self.intruders.append(Intruder(intruder_position, self.__next_intruder_num, self.__region_size, self.__max_exposed_time))
        self.__next_intruder_num += 1

    def get_result(self):
        '''Get the final result of this test.'''
        return self.__test_record

    def _move(self, cmd, one_plane):
        '''Move the plane by identifiy the number of the plane list.'''
        try:
            one_plane.move(cmd)
            #add the endangerous time. To help calculate the reward of MCST algorithem
            if is_endangerous(self.bases, one_plane):
                self.__test_record.add_endangerous(self.simulate_time)
                self.step_info['endangerous'][one_plane.num] += 1
                assert self.step_info['endangerous'][one_plane.num] <= 1
            return 0 #if normal
        except UAV_exception.PlaneLowPower, EXC:
            self.__plane_lost_handler(EXC.plane)
            return -1   #if plane lost
        except UAV_exception.MoveOutOfRegion,EXC:
            print EXC
            assert False
            return 0 #if normal

    def __intruder_identified_handler(self,intruder):
        '''Move out the identified intruder from intruders list and record.'''
        if self.show_info:
            print 'The intruder is exposed! ', intruder
        self.step_info['intruder_exposed'] += 1
        del self.intruders[self.intruders.index(intruder)]
        self.__test_record.add_intruder_time(intruder.get_live_time(),self.simulate_time)
    def __plane_lost_handler(self,plane):
        '''Move out the lost plane from planse list and record.'''
        self.end_simulation = True
        self.__test_record.add_lost_plane(self.simulate_time)
        self.step_info['plane_lost'][plane.num] += 1
        assert self.step_info['plane_lost'][plane.num] <= 1
        self.planes.remove(plane)
        if len(self.planes) <= 0:
            self.__test_record.mission_failed()
            self.__test_record.add_endangerous(self.simulate_time)
            if self.show_info:
                print self.__test_record

    def test(self, special_intruder_positions = None):
        found_intruder = 0
        _null_info_dict = {}
        for _plane in self.planes:
            _null_info_dict[_plane.num] = 0
        self.step_info = {'plane_lost':deepcopy(_null_info_dict), 'find_intruder':0, 'intruder_exposed':0, 
                          'endangerous':deepcopy(_null_info_dict), 'intruder_add_life_time':0}      #information of each step
        self.simulate_time = 0

        def clear_step_info():
            self.step_info['plane_lost'] = deepcopy(_null_info_dict)
            self.step_info['find_intruder'] = 0
            self.step_info['intruder_exposed'] = 0
            self.step_info['endangerous'] = deepcopy(_null_info_dict)
            self.step_info['intruder_add_life_time'] = 0
        def rand_decid():
            return random.randint(0,1)
        def rand_posit(region):
            return (random.randint(0,region[0]-1), random.randint(0,region[1]-1))

        #initial the algorithem
        self.__decide_algorithem.initiate(deepcopy(self.planes),deepcopy(self.bases),self.__region_size,self.__max_plane_battery,self.__max_exposed_time, self.__plane_sight, self.__max_semo_intruder, self.__target_move)

        #add spercific intruders based on the special_intruder_positions
        if special_intruder_positions != None:
            for special_intruder_position in special_intruder_positions:
                self.__add_intruder(special_intruder_position)     #add the spercific intruder
                if self.show_info:
                    print 'An intruder has came!', self.intruders[-1]
        #start test
        while found_intruder < self.__all_intruder_num and len(self.planes) and self.simulate_time <= self.max_simulate_time:
            self.simulate_time += 1

            if self.end_simulation:
                break
            #add intruder randomlly if posibile
            if special_intruder_positions == None and self.__next_intruder_num < self.__all_intruder_num and len(self.intruders) < self.__max_semo_intruder: 
                self.__add_intruder(rand_posit(self.__region_size))
                if self.show_info:
                    print 'An intruder has came!', self.intruders[-1]
            elif self.show_info:
                print 'We decide not to add random intruder this time!'

            #move the intruder randomly
            if self.__target_move:
                for intrd in self.intruders:
                    intrd.move(random.choice(intrd.moveable_direction()))
                    if self.show_info:
                        print 'The intruder has moved to ', intrd

            #Base charging
            for base in self.bases:
                base.charge(self.planes)

            #try to search intruders
            found_intruders_position = []
            for one_plane in self.planes:
                #search for whether intruder is exposed
                try:
                    one_plane.find_intruders(self.intruders)
                    if one_plane.find_intruder:
                        found_intruders_position.append(one_plane.intruder_position)
                        self.__test_record.add_find_intruder(self.simulate_time)
                        self.step_info['find_intruder'] += 1
                        if self.show_info:
                            print one_plane, "find an intruder at ", one_plane.intruder_position
                except UAV_exception.IntruderExposed, EXC:
                    self.__intruder_identified_handler(EXC.intruder)
                    found_intruder += 1

            #return step information to algorithm in case it needs
            self.__decide_algorithem.get_info(self.step_info)
            clear_step_info()

            from quantum_uct_search import QuantumUCTControl
            #use decide algorithem to make decisions
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
            #if not isinstance(self.__decide_algorithem, QuantumUCTControl): #use single process if it isn't UCT algo
            if True:
                #single process
                for one_plane in self.planes:
                    #algorithem move the plane one by one
                    _move_cmd = self.__decide_algorithem.decide(one_plane, self.planes, self.bases, found_intruders_position)
                    if self.show_info:
                        print one_plane, "move to ", _move_cmd
                    self._move(_move_cmd, one_plane)
                #end single process

            else:    #use multiprocess if it's UCT algo   
                #multi-processes-----------failed!       
                main_pipes = []
                processes = []
                #set and initialize all the processes
                for _one_plane in self.planes:
                    new_pipe = mul.Pipe()
                    main_pipes.append(new_pipe[0])
                    new_process = mul.Process(target=multi_process_decide, args=(new_pipe[1],))
                    new_process.start()
                    processes.append(new_process)
                    new_pipe[0].send(self.__decide_algorithem)
                    new_pipe[0].send(_one_plane)
                    new_pipe[0].send(self.planes)
                    new_pipe[0].send(self.bases)
                    new_pipe[0].send(found_intruders_position)

                #get returned cmd and make the move                
                _move_cmd_list = []
                for main_pipe in main_pipes:
                    _move_cmd_list.append(main_pipe.recv())

                #move the plane base on the _cmd_list
                for _one_plane_ii in range(len(self.planes)-1, -1, -1):
                    _one_plane = self.planes[_one_plane_ii]
                    if self.show_info:
                        print _one_plane, "move to ", _move_cmd_list[_one_plane_ii]
                    status = self._move(_move_cmd_list[_one_plane_ii], _one_plane)

                #end multi-processes-----------failed!


            #Intruder adding their living(unexposed) time
            for intruder in self.intruders:
                intruder.add_live_time()
                self.__test_record.add_intruder_live_time()
                self.step_info['intruder_add_life_time'] += 1
        if self.show_info:
            print self.__test_record
        #save record
        self.__test_record.write_to_file()
