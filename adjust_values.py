# Copyright (c) 2018-2021 NORCE, All Rights Reserved. DIGIRES (PhD Wang)

import random
import sys

import numpy as np

from fitvalue import step_rate as calculate
from fitvalue import step_rate_high as calculate1

# single step adjustment with fixed ratio

# import online-learning methods to adjust estimated NPV at whole period or mutiple time periods


class AdjustValues(object):
    def __init__(self, Nw):
        self.father_nodes = []
        self.Nw = Nw

        # cal argvs
        self.original_npv = []
        self.total_ghr = []
        self.initial_hs = []
        self.total_g = []
        self.hs = []
        self.hr = []

    # 1. func( original_npv[] )  # whole period
    def value_v1(self):
        print("-----------value_v1---------")
        foo = calculate.get_value(self.original_npv, self.Nw)
        foo1 = calculate1.get_value(self.original_npv, self.Nw)
        return max(foo, foo1)

    # 2. func( total_ghr[] ) + func( initial_hs[] ) # two periods
    def value_v2(self):
        print("-----------value_v2---------")
        foo = calculate.get_value(self.total_ghr, self.Nw) \
            + calculate.get_value(self.initial_hs, self.Nw)
        return foo
        #foo1 = calculate1.get_value(self.total_ghr, self.Nw) \
            #+ calculate1.get_value(self.initial_hs, self.Nw)
        #return max(foo, foo1)

    # 3. total_ghr[now] + [hs] 
    def value_v3(self):
        print("-----------value_v3---------")
        np_ary = np.array(self.hs, dtype=float)
        col = np_ary.shape[1]
        input_argvs = [list(np_ary[:, index]) for index in range(col)]

        foo = calculate.get_value(self.total_ghr, self.Nw) + \
            sum([calculate.get_value(item, self.Nw) for item in input_argvs])
        return foo
        #foo1 = calculate1.get_value(self.total_ghr, self.Nw) + \
            #sum([calculate1.get_value(item, self.Nw) for item in input_argvs])

        #return max(foo, foo1)

    # 4. total_g[now] + [hr + hs] 
    def value_v4(self):
        print("-----------value_v4---------")
        last_length = len(self.hr[-1])
        argv_ary = [(self.hr[i][-last_length:] if last_length !=
                     0 else []) + self.hs[i] for i in range(len(self.hr))]
        np_ary = np.array(argv_ary, dtype=float)
        col = np_ary.shape[1]
        input_argvs = [list(np_ary[:, index]) for index in range(col)]

        foo = self.total_g[-1] + sum([calculate.get_value(item, self.Nw)
                                      for item in input_argvs])
        foo1 = self.total_g[-1] + sum([calculate1.get_value(item, self.Nw)
                                      for item in input_argvs])

        return max(foo, foo1)

    # 5. total_g[now] + func(original_npv[] - total_g[])
    def value_v5(self, adjust_values):
        max_index = adjust_values.index(max(adjust_values))
        print('\n[ MAX VALUE INDEX = ', max_index, ']\n')
        return max(adjust_values)

    # adjust_values[]
    def get_all(self, father_nodes):
        self.father_nodes = father_nodes
        self.original_npv = []
        self.total_ghr = []
        self.initial_hs = []
        self.total_g = []
        self.hr = []
        self.hs = []

        for item in father_nodes:
            self.original_npv.append(item['original_npv'])
            self.total_ghr.append(item['total_ghr'])
            self.initial_hs.append(item['initial_hs'])
            self.total_g.append(item['total_g'])
            self.hr.append(item['hr'])
            self.hs.append(item['hs'])

        adjust_values = []
        adjust_values.append(self.value_v1())
        adjust_values.append(self.value_v2())
        adjust_values.append(self.value_v3())
        # adjust_values.append(self.value_v4())
        value_v5 = self.value_v5(adjust_values)
        adjust_values.append(value_v5)

        return adjust_values
