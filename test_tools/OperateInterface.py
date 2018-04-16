#!/usr/bin/python
#-*-coding:utf-8-*-
class OperateInterface(object):
    def initiate(self,planes,bases,region_size,max_plane_battery,intruder_exposed_time, plane_sight, max_semo_intruder, target_move):
        assert 0, 'Must choose an algorithem to test!'

    def decide(self,plane, planes, bases, found_intruders_position):
        '''This function must return the moveable command for the plane.'''
        assert 0, 'Must choose an algorithem to test!'
        return cmd

    def get_info(self, step_info):
        '''algorithem can get the info of this time if needed.'''
