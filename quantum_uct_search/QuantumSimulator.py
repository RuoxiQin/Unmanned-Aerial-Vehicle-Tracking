#!/usr/bin/python
#-*-coding:utf-8-*-
#量子模型的主要逻辑，使用递归法实现树搜索

from uct_search_algorithm.UCTTreeNode import UCTTreeNode
from copy import deepcopy
import UAV_exception
import random
from test_tools.tools import *
import math
import UAV_exception

class QuantumSimulator(object):
    '''This is the quantum simulator.'''
    def __init__(self, prob_grid, partner_preference, region_size, simulating_plane_num, planes_list, 
                 base, max_T, max_D, gama, reward_find, reward_endangerous, 
                 max_plane_battery = 20, plane_sight = 1, CP = 0.5, show_info = False, intruders_position = None):
        self.prob_grid = prob_grid
        self.region_size = region_size
        self.partner_preference = partner_preference
        self.simulating_plane_num = simulating_plane_num  
        for plane in planes_list:
            if plane.num == self.simulating_plane_num:
                self.simulating_plane = plane
                break
        self.initial_planes = planes_list
        self.max_plane_battery = max_plane_battery
        self.plane_sight = plane_sight
        self.show_info = show_info
        self.max_T = max_T
        self.max_D = max_D
        self.gama = gama
        self.CP = CP
        self.reward_find = reward_find
        self.base = base
        self.reward_endangerous = reward_endangerous
        self.intruders_position = intruders_position
        self.root = UCTTreeNode({"visit_time":0, "average_benefit":0}, None, self.simulating_plane.moveable_direction(), None)
        return super(QuantumSimulator, self).__init__()

    def UCTPlan(self):
        '''start UCT plan'''
        for t in range(self.max_T):
            prob_grid = deepcopy(self.prob_grid)
            initial_planes = deepcopy(self.initial_planes)
            for plane in initial_planes:
                if plane.num == self.simulating_plane_num:
                    self.simulating_plane = plane
                    break
            self.tree_policy(prob_grid, self.root, initial_planes, 0)
            if self.show_info:
                print "In simulating one move"
                display_region(self.prob_grid.pdg)
                pass
        if self.root.children.values():
            #if there is someway to go
            CMD = sorted(self.root.children.values(), key = lambda child: child.data["average_benefit"])[-1].action
            return CMD
        else:
            #if it already used up power and ready to crush
            return random.choice(self.simulating_plane.moveable_direction())

    def tree_policy(self, prob_grid, node, planes, D):
        '''This is the tree policy'''
        if D >= self.max_D:
            #meet the D limitation and return q=0
            return 0 
        if node.has_untried_moves():
            #if it is leaf, then return q from default policy
            for plane in planes:
                if plane.num == self.simulating_plane_num:
                    #simulating plane
                    try:
                        simulating_action = random.choice(node.untried_moves)
                        plane.move(simulating_action)
                        moveable_direction = plane.moveable_direction()
                        assert moveable_direction
                    except UAV_exception.PlaneLowPower, EXC:
                        q_total = self.reward_endangerous
                        self.update_node(node, q_total)
                        #print EXC.plane, 'crushed!'
                        return q_total
                    except UAV_exception.MoveOutOfRegion,EXC:
                        assert 0
                else:
                    #other planes:
                    try:
                        CMD = self.partner_preference.decide(prob_grid, plane, planes)
                        plane.move(CMD)
                    except UAV_exception.PlaneLowPower, EXC:
                        plane.get_charged()
                        plane.move(CMD)
            #charge all planes
            self.base.charge(planes)
            #get reward
            new_planes_position = [plane.position for plane in planes]
            total_this_round_reward = self.reward_find * prob_grid.get_all_prob_reward(new_planes_position)
            #add endangerous reward
            if is_endangerous([self.base], self.simulating_plane):
                total_this_round_reward += self.reward_endangerous
            #update pdg
            prob_grid.update_pdf_without_real_feedback(new_planes_position)
            if self.show_info:
                print "In tree policy, in leaf node."
                print "Plane", plane.num ," decide to move ", simulating_action
                display_region(prob_grid.pdg)
                pass
            #recurcivly start next round
            q_total = total_this_round_reward + self.gama * self.default_policy(prob_grid, planes, D+1)
            #generate new node            
            new_node = UCTTreeNode({"visit_time":0, "average_benefit":0}, node, moveable_direction, simulating_action)
            #this is weired!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            node.untried_moves.remove(simulating_action)
            node.children[simulating_action] = new_node
            self.update_node(new_node, q_total)
            self.update_node(node, q_total)
            return q_total
        #else it is normal node. apply UCB1 and simulate other plane       
        for plane in planes:
            if plane.num == self.simulating_plane_num:
                #simulating plane
                try:
                    assert node.children.values()
                    simulating_action = sorted(node.children.values(), key = self._choose_priority_calculate_rule)[-1].action
                    plane.move(simulating_action)
                except UAV_exception.PlaneLowPower, EXC:
                    q_total = self.reward_endangerous
                    self.update_node(node, q_total)
                    #print EXC.plane, 'crushed!'
                    return q_total
            else:
                #other planes:
                try:
                    CMD = self.partner_preference.decide(prob_grid, plane, planes)
                    plane.move(CMD)
                except UAV_exception.PlaneLowPower, EXC:
                    plane.get_charged()
                    plane.move(CMD)
        #charge all planes
        self.base.charge(planes)
        #get reward
        new_planes_position = [plane.position for plane in planes]
        total_this_round_reward = self.reward_find * prob_grid.get_all_prob_reward(new_planes_position)
        #add endangerous reward
        if is_endangerous([self.base], self.simulating_plane):
            total_this_round_reward += self.reward_endangerous
        #update pdg
        prob_grid.update_pdf_without_real_feedback(new_planes_position)
        if self.show_info:
            print "In tree policy, in normal choose."
            print "Plane", plane.num ," decide to move ", simulating_action
            display_region(prob_grid.pdg)
            pass
        #recurcivly start next round
        q_total = total_this_round_reward + self.gama * self.tree_policy(prob_grid, node.children[simulating_action], planes, D+1)
        self.update_node(node, q_total)
        return q_total


    def default_policy(self, prob_grid, planes, D):
        '''this is the default policy. it returns q_total'''
        if D < self.max_D:
            for plane in planes:
                if plane.num == self.simulating_plane_num:
                    #simulating plane
                    try:
                        simulating_action = random.choice(plane.moveable_direction())
                        plane.move(simulating_action)
                    except UAV_exception.PlaneLowPower, EXC:
                        q_total = self.reward_endangerous
                        #print EXC.plane, 'crushed!'
                        return q_total
                else:
                    #other planes:
                    try:
                        CMD = self.partner_preference.decide(prob_grid, plane, planes)
                        plane.move(CMD)
                    except UAV_exception.PlaneLowPower, EXC:
                        plane.get_charged()
                        plane.move(CMD)
            #charge all planes
            self.base.charge(planes)
            #get reward
            new_planes_position = [plane.position for plane in planes]
            total_this_round_reward = self.reward_find * prob_grid.get_all_prob_reward(new_planes_position)
            #add endangerous reward
            if is_endangerous([self.base], self.simulating_plane):
                total_this_round_reward += self.reward_endangerous
            #update pdg
            prob_grid.update_pdf_without_real_feedback(new_planes_position)
            if self.show_info:
                print "In default policy."
                print "Plane", plane.num ," decide to move ", simulating_action
                display_region(prob_grid.pdg)
                pass
            #recurcivly start next round
            q_total = total_this_round_reward + self.gama * self.default_policy(prob_grid, planes, D+1)
            return q_total
        else:
            return 0

    def update_node(self, node, q_total):
        '''this is the updating procedure in backpropagation'''
        node.data["average_benefit"] = (node.data["average_benefit"] * node.data["visit_time"] + q_total) / (node.data["visit_time"] + 1)
        node.data["visit_time"] += 1

    def _choose_priority_calculate_rule(self, node):
        assert type(node) is UCTTreeNode
        Q_value = node.data["average_benefit"] + 2 * self.CP * math.sqrt((2 * math.log(node.parent.data["visit_time"]) / node.data["visit_time"]))
        dif = abs(abs(node.data["average_benefit"]) - abs(2 * self.CP * math.sqrt((2 * math.log(node.parent.data["visit_time"]) / node.data["visit_time"]))))
        dif_por = 2 * dif / (abs(node.data["average_benefit"]) + abs(2 * self.CP * math.sqrt((2 * math.log(node.parent.data["visit_time"]) / node.data["visit_time"]))))
        return Q_value
