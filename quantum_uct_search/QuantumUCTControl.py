#!/usr/bin/python
#-*-coding:utf-8-*-

"""
The control interface of our algorithm.
"""

from copy import deepcopy
from QuantumSimulator import QuantumSimulator
from PartnerPreference import PartnerPreference
from ProbabilityGrid import ProbabilityGrid
from test_tools.OperateInterface import OperateInterface


class QuantumUCTControl(OperateInterface):
    '''this is the quantum UCT algo'''

    #self.partner_preference = PartnerPreference(base, plane_sight, D_max, region_size)

    def __init__(self, CP=0.5, max_trajectory = 200, max_depth = 8,
                 reward_gather = 2, reward_find = 0.5, reward_endangerous = -0.1,
                 reward_lost_plane = -1, reward_intruder_life_plus = -0.1, 
                 show_info = False, gama = 0.9):
        self.CP = CP   #CP is used to adjust the priority of explore
        self.max_T = max_trajectory
        self.max_D = max_depth
        self.reward_gather = reward_gather
        self.reward_find = reward_find
        self.reward_endangerous = reward_endangerous
        self.reward_lost_plane = reward_lost_plane
        self.show_info = show_info
        self.reward_intruder_life_plus = reward_intruder_life_plus
        self.gama = gama
        return super(QuantumUCTControl, self).__init__()

    def initiate(self,planes,bases,region_size,max_plane_battery,intruder_exposed_time, plane_sight, max_semo_intruder, target_move):
        self.bases = deepcopy(bases)
        self.region_size = region_size
        self.max_plane_battery = max_plane_battery
        self.intruder_exposed_time = intruder_exposed_time
        self.plane_sight = plane_sight
        self.max_semo_intruder = max_semo_intruder
        self.target_move = target_move
        self.partner_preference = PartnerPreference(bases[0], plane_sight, self.max_D, region_size)
        self.prob_grid = ProbabilityGrid(region_size, [plane.position for plane in planes], plane_sight, None)

    def decide(self,plane, planes, bases, found_intruders_position):
        if planes.index(plane) == 0:
            if found_intruders_position:
                self.prob_grid.update_pdf_to_spercific_position(found_intruders_position[0])
            else:
                self.prob_grid.update_pdf_with_no_intruder([one_plane.position for one_plane in planes])
        if self.show_info:
            print "Real distribution."
            display_region(self.prob_grid.pdg)
            pass
        qt_simulator = QuantumSimulator(self.prob_grid, self.partner_preference, self.region_size, plane.num, planes, 
                 bases[0], self.max_T, self.max_D, self.gama, self.reward_find, self.reward_endangerous, 
                 self.max_plane_battery, self.plane_sight, self.CP, self.show_info, found_intruders_position)
        CMD = qt_simulator.UCTPlan()
        return CMD
