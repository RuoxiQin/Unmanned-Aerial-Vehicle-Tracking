#!/usr/bin/python
#-*-coding:utf-8-*-
class ResultRecord(object):
    '''This class contains the record of the test.'''
    def __init__(self, store_result = False, file_name = 'SimulateResult.txt'):
        self.intruder_num = 0
        self.lost_plane = 0
        self.average = 0.0
        self.failed = False
        self.sqrsum = 0.0
        self.endangerous = 0
        self.find_intruder_times = 0;
        self.total_intruder_live_time = 0
        self.store_result = store_result
        self.file_name = file_name
        self._record_list = []
        return super(ResultRecord, self).__init__()

    def add_lost_plane(self, simulate_time):
        self.lost_plane += 1
        if self.store_result:
            self._record_list.append('lost\t'+str(simulate_time))

    def add_intruder_time(self, intruder_time, simulate_time):
        self.average = (self.average*self.intruder_num + intruder_time) / (self.intruder_num + 1)
        self.sqrsum += intruder_time ** 2
        self.intruder_num += 1
        if self.store_result:
            self._record_list.append('exposed\t'+str(simulate_time))

    def add_intruder_live_time(self):
        self.total_intruder_live_time += 1

    def add_find_intruder(self, simulate_time):
        '''if any plane observes an intruder, then this function records it.'''
        self.find_intruder_times += 1;
        if self.store_result:
            self._record_list.append('find\t'+str(simulate_time))

    def add_endangerous(self, simulate_time):
        '''This function add the time when plane is endangerous.'''
        self.endangerous += 1
        if self.store_result:
            self._record_list.append('endangerous\t'+str(simulate_time))

    def result(self):
        #get the result of the record
        if self.intruder_num:
            return {'average':self.average, 'deviation':math.sqrt(self.sqrsum/float(self.intruder_num) -  (self.average**2))}
        else:
            return {'average':0, 'deviation':0}

    def __str__(self):
        if self.failed:
            return 'Mission failed! We have lost all planes!'
        else:
            return 'Mission accomplished:\n\tFound %d intruders\n\tAverage time of finding: %.3f\n\tStandard deviation: %.3f\n\tWith %d plane(s) lost!' % (self.intruder_num, self.average, self.result()['deviation'], self.lost_plane)
    
    def mission_failed(self):
        self.failed = True

    def write_to_file(self):
        '''This function should be added at the end of simulation and it will save the record.'''
        if self.store_result:
            file_object = open(self.file_name, 'w')
            for _record in self._record_list:
                file_object.write(_record+'\n')
            file_object.close()
