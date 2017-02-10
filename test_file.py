#!/usr/bin/python
#-*-coding:utf-8-*-

'''This is the test file.'''

if __name__ == "__main__":
    import test_tools
    import UAV_search_algorithem
    from uct_search_algorithm import UCTControl
    from quantum_uct_search.QuantumUCTControl import QuantumUCTControl

    #set all work
    '''
    all_work = {'8x8T100D3':{'name':'8x8T100D3','T':100,'D':3,'test_times':0,
                             'size':(20,20),'base_lists':[(10,10)], 
                             'plane_lists':[(1,1),(18,18),(1,18),(18,1)]},
                '8x8T100D6':{'name':'8x8T100D6','T':100,'D':6,'test_times':0,
                             'size':(20,20),'base_lists':[(10,10)], 
                             'plane_lists':[(1,1),(18,18),(1,18),(18,1)]},
                '8x8T200D3':{'name':'8x8T200D3','T':200,'D':3,'test_times':0,
                             'size':(20,20),'base_lists':[(10,10)], 
                             'plane_lists':[(1,1),(18,18),(1,18),(18,1)]},
                '8x8T200D6':{'name':'8x8T200D6','T':200,'D':6,'test_times':0,
                             'size':(20,20),'base_lists':[(10,10)], 
                             'plane_lists':[(1,1),(18,18),(1,18),(18,1)]},
                }
    '''

    all_work = {'8x8T200D3':{'name':'8x8T200D3','T':50,'D':3,'test_times':0,
                             'size':(8,8),'base_lists':[(4,4)], 
                             'plane_lists':[(1,1),(4,4),(1,4),(4,1)]}
                }



    #read work schedule
    schedule_file = open("simulatingSchedule.txt", 'a+')
    finished_work_list = []
    for line in schedule_file.readlines():
        finished_work_list.append(line)
    schedule_file.close()
    #find out what work remained to be done
    for finished_work in finished_work_list:
        all_work[finished_work.strip('\n')]['test_times'] += 1
    #start doing the remained works
    work = sorted(all_work.values(), key = lambda work:work['test_times'])[0]
    while work['test_times'] < 1:
        #record this time
        times = work['test_times']
        #start simulation
        test_setting = {'region_size':work['size'], 'base_position_list':work['base_lists'], 'plane_position_list':work['plane_lists'] , 
                        'all_intruder_num':1, 'max_semo_intruder':1, 'target_move':True ,
                        'max_plane_battery' :5, 'max_exposed_time':3000,
                        'plane_sight':1, "show_info":True,
                        "max_simulate_time":100,
                        'store_result':True, 'file_name':work['name']+'('+str(times)+')v2_0.txt'}

        #algorithem setting v1_0
        #algorithem_setting = {"CP":0.3, "max_trajectory":work['T'], "max_depth":work['D'],
        #                        "reward_gather":1, "reward_intruder_life_plus": -0.2,
        #                        "reward_find":0.2 ,"reward_endangerous":-2, "reward_lost_plane":-2,
        #                        "show_info":False, "gama":0.9}

        #algorithem setting v2_0
        algorithem_setting = {"CP":0.5, "max_trajectory":work['T'], "max_depth":work['D'],
                                "reward_gather":2, "reward_intruder_life_plus": 0,
                                "reward_find":1 ,"reward_endangerous":-1.5, "reward_lost_plane":0,
                                "show_info":False, "gama":0.9}


        algorithem = QuantumUCTControl(**algorithem_setting)
        test = test_tools.TestInitiator(algorithem, test_setting)
        record = test.get_result().result()
        #write record
        schedule_file = open("simulatingSchedule.txt", 'a+')
        schedule_file.write(work['name'] + '\n')
        schedule_file.close()
        #find the next work to do
        work['test_times'] += 1
        work = sorted(all_work.values(), key = lambda work:work['test_times'])[0]
        print work['name'] + '('+str(times)+')' + 'finished! Start next one...'
    print 'All work finished!'


