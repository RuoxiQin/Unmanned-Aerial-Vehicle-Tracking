'''This module contains the exception of the UAV search test.'''

class UAVException(Exception):
    '''This is the category of the UAVException.'''
    def __str__(self):
        return 'An exception of UAV search test occurs! Please contact the designner for help!'

class PlaneLowPower(UAVException):
    def __init__(self, plane):
        self.plane = plane
        return super(PlaneLowPower, self).__init__()

    def __str__(self):
        return self.plane.__str__()+ ' crashed because it used up power!' 

class MoveOutOfRegion(UAVException):
    direction = {'L':'LEFT', 'R':'RIGHT', 'U':'UP', 'D':'DOWN'}
    def __init__(self, component,cmd):
        self.cmd = cmd
        self.component = component
        return super(MoveOutOfRegion, self).__init__()

    def __str__(self):       
        return self.component.__str__()+ (' can not move %s!' % self.__class__.direction[self.cmd])

class IntruderExposed(UAVException):
    def __init__(self, intruder):
        self.intruder = intruder
        return super(IntruderExposed, self).__init__()

    def __str__(self):
        return self.intruder.__str__()+ ( ' has been exposed!' )

class LostAllPlane(UAVException):
    def __str__(self):
        return 'Mission failed. We have lost all planes!'