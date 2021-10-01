# # Copyright (c) 2018-2021 NORCE, All Rights Reserved. DIGIRES (PhD Wang)
import math
import random
import sys

import xlwt

import adjust_values as adjust
# helper models
# import helper_v1 as helper
import initial_values as helper
from untils import record

sys.dont_write_bytecode = True
sys.setrecursionlimit(1000000)


class Search(object):
    def __init__(self, begin_state, drillingtime, limit_travel, limit_step, limit_search):
        # given initital argvs
        self.begin_state = begin_state
        self.drillingtime = drillingtime
        self.limit_travel = limit_travel
        self.limit_step = limit_step
        self.limit_search = limit_search

        '''
        for run astar search argvs
        '''

        # all nodes
        self.all_nodes = []
        self.nodes_count = 0

        # astar search argvs
        self.open_table = []
        self.close_table = []
        self.total_table = []
        self.out_open = []
        self.out_close = []
        self.removed_nodes = []

        # using predication.helper
        self.predict = helper.PreDictValue(drillingtime)  # original_npv  Class

        # using fitvalue
        self.fitvalue = adjust.AdjustValues(
            len(begin_state['name']))  # lens(begin_state)=Nw

        # cut levels_num
        self.cut_num = None

    def get_new_state(self, schedule):

        name = []
        # count_num: count for 0.5
        count_num = 0
        for item in schedule:
            name.append(item[0])
            if 0.5 == item[1]:
                count_num += 1
        new_state = {
            'poro': self.begin_state['poro'],
            'permx': self.begin_state['permx'],
            'multflt': self.begin_state['multflt'],
            'name': name,
            'drillingtime': schedule
        }
        # number of remaining wells
        Ns = len(schedule) - (count_num + 1)
        return new_state, Ns

    def create_node(self, schedule, father_indexs, father_nodes):
        new_state, Ns = self.get_new_state(schedule)
        initial_data, ranked_producers, ranked_injectors, next_actions = self.predict.get_initial_data(
            new_state, Ns)

        new_node = {
            'schedule': schedule,
            'total_g': initial_data['total_g'],
            'initial_hr': initial_data['initial_hr'],
            'total_ghr': initial_data['total_ghr'],
            'initial_hs': initial_data['initial_hs'],
            'original_npv': initial_data['original_npv'],
            'father_indexs': father_indexs,
            'g': initial_data['g'],
            'hr': initial_data['hr'],
            'hs': initial_data['hs'],
            'index': self.nodes_count,
            'ranked_producers': ranked_producers,
            'ranked_injectors': ranked_injectors,
            'next_actions': next_actions
        }
        print('\n{0:*^100}'.format(' [State = %d]' % self.nodes_count))
        # father_nodes.append(new_node)
        foo_father = father_nodes.copy()
        foo_father.append(new_node)
        adjust_values = self.fitvalue.get_all(foo_father)

        # Select online learning technique
        if Ns <= 3:
            check_value = adjust_values[0] # 0 or 2
        else:
            check_value = adjust_values[0]

        new_node['adjust_values'] = adjust_values
        new_node['check_value'] = check_value

        record.Record(self.drillingtime).write_format(new_node)

        self.all_nodes.append(new_node)
        self.nodes_count += 1
        return self.nodes_count - 1

    def get_open_max_index(self):
        max_index = self.open_table[0]
        max_value = self.all_nodes[max_index]['check_value']
        for item in self.open_table:
            check_value = self.all_nodes[item]['check_value']
            if check_value > max_value:
                max_value = check_value
                max_index = item
        return max_index

    def match_limit_travel(self, index):
        if -1 == self.limit_travel:
            return False

        step = 0
        for item in self.all_nodes[index]['schedule']:
            if self.drillingtime == item[1]:
                step += 1
            else:
                break

        if step > self.limit_travel:
            print("search step: ", self.limit_travel)
            return True

    def match_limit_step(self, index):
        return False

    def match_limit_search(self):
        if -1 == self.limit_search:
            return False
        length = len(self.open_table) + len(self.close_table)
        return length > self.limit_search

    def match_end_search(self, index):
        for item in self.all_nodes[index]['schedule']:
            if 0.5 == item[1]:
                return False
        return True

    def get_adjacs(self, max_index):
        father_node_schedule = self.all_nodes[max_index]['schedule']
        pre_schedules = []
        pos_worked = 0
        for index, item in enumerate(father_node_schedule):
            if self.drillingtime == item[1]:
                pos_worked = index
                pre_schedules.append(item)
            else:
                break

        pre_schedules = pre_schedules[:-1]

        father_indexs = self.all_nodes[max_index]['father_indexs'].copy()
        father_indexs.append(max_index)
        father_nodes = [self.all_nodes[i] for i in father_indexs]

        adjac_indexs = []
        length = len(father_node_schedule)
        for i in range(pos_worked, length):
            now_schedule = [(father_node_schedule[i][0], self.drillingtime)]

            # judge if exit in next_actions
            #if now_schedule[0][0] not in self.all_nodes[max_index]['next_actions']:
                #continue

            fir = True
            for j in range(pos_worked, length):
                if j == i:
                    continue

                e_tuple = (
                    father_node_schedule[j][0],
                    self.drillingtime if fir == True else 0.5
                )

                fir = False
                now_schedule.append(e_tuple)

            now_schedule = pre_schedules + now_schedule
            node_indexs = self.create_node(
                now_schedule, father_indexs, father_nodes)
            adjac_indexs.append(node_indexs)

        adjac_indexs_for_table = adjac_indexs
        if self.cut_num != None and len(adjac_indexs) > self.cut_num:
            adjac_indexs = sorted(adjac_indexs, key=lambda v: self.all_nodes[v]['check_value'], reverse=True)
            print("ranked wells based on estimated NPV: ", adjac_indexs)
            print("removed wells: ", adjac_indexs[self.cut_num:])
            self.removed_nodes += adjac_indexs[self.cut_num:]
            adjac_indexs = adjac_indexs[:self.cut_num]
        return adjac_indexs, adjac_indexs_for_table

    def travel_search(self, first_flag, end_flag):
        if True == end_flag or 0 == len(self.open_table):
            end_flag = True
            return

        max_index = self.get_open_max_index()

        self.open_table.remove(max_index)
        self.close_table.append(max_index)

        if True == self.match_limit_travel(max_index) \
                or True == self.match_limit_step(max_index) \
                or True == self.match_limit_search():
            end_flag = True
            return

        if True == self.match_end_search(max_index):
            end_flag = True
            self.out_open.append(self.open_table.copy())
            self.out_close.append(self.close_table.copy())
            return

        adjac_indexs, adjac_indexs_for_table = self.get_adjacs(max_index)
        self.open_table += adjac_indexs
        self.out_open.append(self.open_table.copy())
        self.out_close.append(self.close_table.copy())
        self.total_table.append(adjac_indexs_for_table.copy())
        self.travel_search(first_flag, end_flag)

    def entry(self):
        root_node_index = self.create_node(
            self.begin_state['drillingtime'], [], [])

        self.open_table.append(root_node_index)
        self.total_table.append([root_node_index])
        self.travel_search(True, False)
