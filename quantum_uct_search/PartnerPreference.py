#!/usr/bin/python
#-*-coding:utf-8-*-
#此类用于根据队友周围的情况，模拟做出队友的运动选择

import test_tools

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
