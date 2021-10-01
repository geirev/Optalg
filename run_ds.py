# Copyright (c) 2018-2021 NORCE, All Rights Reserved. DIGIRES (PhD Wang)

import os
import sys

import pandas as pd
import search
from untils import record
sys.path.append('/home/liwa/Desktop/pipt_old')
sys.path.append('fitvalue')
sys.dont_write_bytecode = True

drillingtime = 10
limit_travel = -1
limit_step = -1
limit_search = 1500

begin_state = {
    'name': ['OP_1', 'OP_2', 'OP_3', 'OP_4', 'OP_5', 'WI_1', 'WI_2', 'WI_3'],
    'drillingtime': [('OP_1', drillingtime), ('OP_2', 0.5), ('OP_3', 0.5),
                     ('OP_4', 0.5), ('OP_5', 0.5), ('WI_1', 0.5), ('WI_2',0.5),('WI_3', 0.5)]
}

if __name__ == '__main__':
    poro = pd.read_csv('./prior_1/prior_poro_101.csv')
    permx = pd.read_csv('./prior_1/prior_permx_101.csv')
    multflt = pd.read_csv('./prior_1/prior_multflt_101.csv')
    
    poro = poro.T.values.tolist()
    permx = permx.T.values.tolist()
    multflt = multflt.T.values.tolist()

    index = 0
    for poro, permx, multflt in zip(poro, permx, multflt):
        begin_state['poro'] = poro
        begin_state['permx'] = permx
        begin_state['multflt'] = multflt
        # A * search
        astar = search.Search(begin_state, drillingtime, limit_travel,
                              limit_step, limit_search)
        astar.entry()

        # record information
        record_obj = record.Record(drillingtime, str(index))
        record_obj.write_to_command(astar.all_nodes, astar.out_open,
                                astar.out_close, astar.total_table,
                                astar.removed_nodes)

        record_obj.write_to_file(astar.all_nodes, astar.total_table,
                             astar.out_close[-1], astar.removed_nodes,
                             os.getcwd() + '/data')
        index += 1
        #if index > 3:
            #break
