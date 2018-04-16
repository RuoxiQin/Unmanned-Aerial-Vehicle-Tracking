#!/usr/bin/python
#-*-coding:utf-8-*-

"""
Update the Probability Distribution Function (PDF)
"""

import random

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
