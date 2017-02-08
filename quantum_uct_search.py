#!/usr/bin/python
#-*-coding:utf-8-*-
'''this algorithm search the region using analogy of quantum'''

import UAV_exception
import test_tools
import UAV_search_algorithem
import math
import random
from copy import deepcopy
import Components
import uct_search_algorithem

#实际上调用的就是这个控制器，但是其实这是一个为满足接口的东西，主要逻辑在其调用的QuantumSimulator里面
class QuantumUCTControl(test_tools.OperateInterface):
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


#量子模型的主要逻辑，使用递归法实现树搜索
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
        self.root = uct_search_algorithem.UCTTreeNode({"visit_time":0, "average_benefit":0}, None, self.simulating_plane.moveable_direction(), None)
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
            if test_tools.is_endangerous([self.base], self.simulating_plane):
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
            new_node = uct_search_algorithem.UCTTreeNode({"visit_time":0, "average_benefit":0}, node, moveable_direction, simulating_action)
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
        if test_tools.is_endangerous([self.base], self.simulating_plane):
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
            if test_tools.is_endangerous([self.base], self.simulating_plane):
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
        assert type(node) is uct_search_algorithem.UCTTreeNode
        Q_value = node.data["average_benefit"] + 2 * self.CP * math.sqrt((2 * math.log(node.parent.data["visit_time"]) / node.data["visit_time"]))
        dif = abs(abs(node.data["average_benefit"]) - abs(2 * self.CP * math.sqrt((2 * math.log(node.parent.data["visit_time"]) / node.data["visit_time"]))))
        dif_por = 2 * dif / (abs(node.data["average_benefit"]) + abs(2 * self.CP * math.sqrt((2 * math.log(node.parent.data["visit_time"]) / node.data["visit_time"]))))
        return Q_value


#此类用于根据队友周围的情况，模拟做出队友的运动选择
class PartnerPreference(object): #haven't tested!!!!!!!!!!!!!!!!!!
    '''This is the partner preference'''
    def __init__(self, base, plane_sight, D_max, region_size):
        self.base = base
        self.plane_sight = plane_sight
        self.D_max = D_max
        self.region_size = region_size
        return super(PartnerPreference, self).__init__()

    def decide(self, prob_grid, decide_plane, planes):
        if decide_plane.battery - test_tools.distance(self.base.position, decide_plane.position) - self.D_max > 2:
            #if there is enough engery
            #calculate left reward
            reward = {'L':0, 'R':0, 'U':0, 'D':0}
            for x in range(decide_plane.position[0], decide_plane.position[0]-self.D_max-self.plane_sight, -1):
                if x < 0:
                    break
                for y in range(decide_plane.position[1]-self.D_max-self.plane_sight, decide_plane.position[1]+self.D_max+self.plane_sight):
                    if 0 <= y < self.region_size[0]:
                        reward['L'] += prob_grid.pdg[x][y]
            #calculate right reward
            for x in range(decide_plane.position[0], decide_plane.position[0]+self.D_max+self.plane_sight):
                if x >= self.region_size[1]-1:
                    break
                for y in range(decide_plane.position[1]-self.D_max-self.plane_sight, decide_plane.position[1]+self.D_max+self.plane_sight):
                    if 0 <= y < self.region_size[0]:
                        reward['R'] += prob_grid.pdg[x][y]
            #calculate up reward
            for y in range(decide_plane.position[1], decide_plane.position[1]-self.D_max-self.plane_sight, -1):
                if y < 0:
                    break
                for x in range(decide_plane.position[0]-self.D_max-self.plane_sight, decide_plane.position[0]+self.D_max+self.plane_sight):
                    if 0 <= x < self.region_size[1]:
                        reward['U'] += prob_grid.pdg[x][y]
            #calculate down reward
            for y in range(decide_plane.position[1], decide_plane.position[1]+self.D_max+self.plane_sight):
                if y >= self.region_size[0]-1:
                    break
                for x in range(decide_plane.position[0]-self.D_max-self.plane_sight, decide_plane.position[0]+self.D_max+self.plane_sight):
                    if 0 <= x < self.region_size[1]:
                        reward['D'] += prob_grid.pdg[x][y]
            for index in range(-1, -5, -1):
                if sorted(reward.keys(), key = lambda cmd: reward[cmd])[index] in decide_plane.moveable_direction():
                    return sorted(reward.keys(), key = lambda cmd: reward[cmd])[index]
            assert 0 #must return something!!!
        else:
            #if it is low power:
            #direct fly to the base
            CMD = test_tools.direct(decide_plane.position, self.base.position)
            return CMD

#此类用于更新PDF
class ProbabilityGrid(object):
    '''this is the probability grid'''
    def __init__(self, region_size, planes_position_list, plane_sight, intruder_position = None):
        '''initialization with no intrder founded or prior experience.'''
        self.region_size = region_size
        self.plane_sight = plane_sight
        if intruder_position:
            #if find an intruder
            self.update_pdf_to_spercific_position(intruder_position)
        else:   #no intruder found
            #calculate probability distribution grid
            diffus_region = self.diffusible_region(planes_position_list)
            #calculate the number of diffusible grid
            num_diffus_able_position = sum([sum(line) for line in diffus_region])
            mean_prob = 1.0 / num_diffus_able_position
            #assign the mean_prob and get the pdg
            self.pdg = [[item * mean_prob for item in line] for line in
                        diffus_region]
        assert 0.999 < sum([sum(col) for col in self.pdg]) < 1.001
        return super(ProbabilityGrid, self).__init__()

    def update_pdf_to_spercific_position(self, intruder_position):
        '''this circumstand is used to update pdg by real feedback.'''
        self.pdg = [[0.0 for y in range(self.region_size[0])] for x in range(self.region_size[1])]
        self.pdg[intruder_position[0]][intruder_position[1]] = 1.0
        assert 0.999 < sum([sum(col) for col in self.pdg]) < 1.001

    def update_pdf_with_no_intruder(self, planes_position_list):
        '''this is used when real feedback shows that there is no intruder'''
        assert 0.999 < sum([sum(col) for col in self.pdg]) < 1.001
        diffus_region = self.diffusible_region(planes_position_list)
        new_pdg = [[0.0 for y in range(self.region_size[0])] for x in range(self.region_size[1])]
        new_all_planes_sight = self.get_all_planes_sight(planes_position_list)
        '''
        if new_get_reward > 0.999:
            print planes_position_list
            for x in range(self.region_size[1]):
                for y in range(self.region_size[0]):
                    if self.pdg[x][y] > 0.99:
                        print "The intruder's probability position is (%d,%d)"\
                                % (x, y)
            assert False
        '''
        #propagate probability
        for x in range(self.region_size[1]):
            for y in range(self.region_size[0]):
                #if (x,y) in new_all_planes_sight:
                    #if this position is in the sight horizon of plane, then it is sure that there is no intruder
                    #continue
                deffus_positions = self.get_diffusible_positions(diffus_region, (x,y))
                if len(deffus_positions) > 0:
                    new_prob = self.pdg[x][y] / float(len(deffus_positions))
                    for deffus_position in deffus_positions:
                        #propagate
                        assert 0 <= deffus_position[0] < self.region_size[1] and 0 <= deffus_position[1] < self.region_size[0]
                        new_pdg[deffus_position[0]][deffus_position[1]] += new_prob
        self.pdg = new_pdg
        now_total_probability = sum([sum(col) for col in self.pdg])
        assert now_total_probability > 0
        if now_total_probability < 1:
            for x in range(self.region_size[1]):
                for y in range(self.region_size[0]):
                    self.pdg[x][y] *= 1.0 / now_total_probability
        assert 0.999 < sum([sum(col) for col in self.pdg]) < 1.001

    def update_pdf_without_real_feedback(self, planes_position_list):
        '''this is used in simulation part, where there is no real feedback.'''
        assert 0.999 < sum([sum(col) for col in self.pdg]) < 1.001
        #all region is diffusible
        diffus_region =[[1 for y in range(self.region_size[0])] for x in range(self.region_size[1])]
        new_pdg = [[0.0 for y in range(self.region_size[0])] for x in range(self.region_size[1])]
        new_all_planes_sight = self.get_all_planes_sight(planes_position_list)
        #propagate probability
        for x in range(self.region_size[1]):
            for y in range(self.region_size[0]):
                deffus_positions = self.get_diffusible_positions(diffus_region, (x,y))
                if len(deffus_positions) > 0:
                    new_prob = self.pdg[x][y] / float(len(deffus_positions))
                    for deffus_position in deffus_positions:
                        #propagate
                        assert 0 <= deffus_position[0] < self.region_size[1] and 0 <= deffus_position[1] < self.region_size[0]
                        new_pdg[deffus_position[0]][deffus_position[1]] += new_prob
        self.pdg = new_pdg
        now_total_probability = sum([sum(col) for col in self.pdg])
        assert now_total_probability > 0
        if now_total_probability < 1:
            for x in range(self.region_size[1]):
                for y in range(self.region_size[0]):
                    self.pdg[x][y] *= 1.0 / now_total_probability
        assert 0.999 < sum([sum(col) for col in self.pdg]) < 1.001
        self.enviroment_decide_simulating_pdg(planes_position_list)

    def enviroment_decide_simulating_pdg(self, planes_position_list):
        '''this is used before planes getting reward. it would change pdg'''
        assert 0.999 < sum([sum(col) for col in self.pdg]) < 1.001
        new_all_planes_sight = self.get_all_planes_sight(planes_position_list)
        total_prob_in_sight = 0.0
        #propagate probability
        for x in range(self.region_size[1]):
            for y in range(self.region_size[0]):
                if (x,y) in new_all_planes_sight:
                    #if this position is in the sight horizon of plane, then there might be an intruder
                    if random.random() <= self.pdg[x][y] / (1 - total_prob_in_sight):
                        #if simulating result is finding the intruder:find a new intruder
                        self.update_pdf_to_spercific_position((x,y))
                        return
                    else: #if simulating result is not finding an intruder
                        total_prob_in_sight += self.pdg[x][y]
                        self.pdg[x][y] = 0.0
        for x in range(self.region_size[1]):
            for y in range(self.region_size[0]):
                self.pdg[x][y] *= 1.0 / (1 - total_prob_in_sight)
        assert 0.999 < sum([sum(col) for col in self.pdg]) < 1.001



    def get_all_prob_reward(self, planes_position_list):
        '''this function return the sum of eaten probability of each UAV'''
        prob_sum = 0.0
        all_planes_sight = self.get_all_planes_sight(planes_position_list)
        for position in all_planes_sight:
            prob_sum += self.pdg[position[0]][position[1]]
        return prob_sum

    def diffusible_region(self, planes_position_list):
        '''This function return the diffusible_region( denoted by 1 if diffusible)'''
        region = [[1 for y in range(self.region_size[0])] for x in range(self.region_size[1])]
        for plane_position in planes_position_list:
            sight_positions = self.get_plane_sight(plane_position)
            for sight_position in sight_positions:
                region[sight_position[0]][sight_position[1]] = 0
        return region

    def get_diffusible_positions(self, diffus_region, position):  ##haven't tested!!!!!!!!!
        '''this function return a list which contain all positions diffusible by given position'''
        x_len = self.region_size[1]
        y_len = self.region_size[0]
        diffus_list = []
        if position[1] - 1 >= 0 and diffus_region[position[0]][position[1]-1]:
            diffus_list.append((position[0], position[1]-1))
        if position[1] + 1 < y_len and diffus_region[position[0]][position[1]+1]:
            diffus_list.append((position[0], position[1]+1))
        if position[0] - 1 >= 0 and diffus_region[position[0]-1][position[1]]:
            diffus_list.append((position[0]-1, position[1]))
        if position[0] + 1 < x_len and diffus_region[position[0]+1][position[1]]:
            diffus_list.append((position[0]+1, position[1]))
        if diffus_region[position[0]][position[1]]:
            diffus_list.append((position[0], position[1]))
        return diffus_list

    def get_plane_sight(self, plane_position):
        '''this function return the position in the plane sight'''
        sight_positions = []
        for sight_x in range(plane_position[0] - self.plane_sight, plane_position[0] + self.plane_sight + 1):
                for sight_y in range(plane_position[1] - self.plane_sight, plane_position[1] + self.plane_sight + 1):
                    if 0 <= sight_x < self.region_size[0] and 0 <= sight_y < self.region_size[1]:
                        sight_positions.append((sight_x, sight_y))
        return sight_positions

    def get_all_planes_sight(self, planes_position):
        '''return all sight positions'''
        all_sight_positions = []
        for plane_position in planes_position:
            sight_positions = self.get_plane_sight(plane_position)
            for sight_position in sight_positions:
                if sight_position not in all_sight_positions:   #this might be wrong!!
                    all_sight_positions.append(sight_position)
        return all_sight_positions



def display_region(region):
    '''This function print the region in the right way'''
    x_length = len(region)
    y_length = len(region[0])
    dis = [[0 for x in range(y_length)] for y in range(x_length)]
    for y in range(y_length):
        for x in range(x_length):
            dis[x][y] = region[y][x]
    for line in dis:
        for x in line:
            print '%.5f\t' % x,
        print '\n',
    print '\n',



if __name__ == "__main__":
    region_size = (8,8)
    max_plane_battery = 50
    plane_sight = 1
    CP = 0.5
    planes_list = [Components.Plane((1,1), 0, region_size, max_plane_battery, plane_sight), 
                   Components.Plane((1,6), 1, region_size, max_plane_battery, plane_sight),
                   Components.Plane((6,1), 2, region_size, max_plane_battery, plane_sight),
                   Components.Plane((6,6), 3, region_size, max_plane_battery, plane_sight)]
    base = Components.Base((4,4), 0, region_size)
    max_T = 100
    max_D = 5
    gama = 0.9
    reward_find = 1
    reward_endangerous = -1.5
    partner_preference = PartnerPreference(base, plane_sight, max_D, region_size)
    Qt_simulator = QuantumSimulator(partner_preference, region_size, 0, planes_list, 
                 base, max_T, max_D, gama, reward_find, reward_endangerous, max_plane_battery,
                 plane_sight, CP, False, None)
    Qt_simulator.UCTPlan()
