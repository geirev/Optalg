# Copyright (c) 2018-2021 NORCE, All Rights Reserved. DIGIRES (PhD Wang)
import math
import random
import numpy as np
import sys
import os
sys.path.append('/home/liwa/Desktop/pipt_old')
from simulator.subsurf_flow import ecl_100
import pandas as pd


class PreDictValue(object):
    def __init__(self, drillingtime):

        self.ecl = ecl_100({'runfile': 'reek', 'startdate': '1/12/1999'})

        self.drillingtime = drillingtime

        # NPV 10 years
        # Report/data index
        num_report = list(range(1, 21))
        num_report.pop(0)
        self.reportdates = [x * drillingtime for x in num_report]
        print("reportdate", self.reportdates)

    def get_initial_gh(self, new_state, Nw, Ns):

      
        # Run the Schlumberger eclipse 100 black oil reservoir simulator
        ind = list(range(len(self.reportdates)))
        assim_ind = ['days', ind]   # ['days', [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]]
        true_order = ['days', self.reportdates]

 

        # Set input parameters from an fwd_sim in the simulation to get predicted data
        self.ecl.setup_fwd_run(new_state, assim_ind, true_order)
        self.ecl.run_fwd_sim(folder=os.getcwd() + '/', wait_for_proc=True)

        # Set economic parameters for objective function (NPV) /evaluation function
        disc = 0.08
        wop = 60
        wgp = 2
        wwp = 5
        wwi = 1
        wellCost = 1e06

        # Calculate initial estimated economic value for each time period
        initial_gh=[]
        for i in range(len(self.reportdates)):
            if i ==0:
                Qop = self.ecl.get_sim_results('FOPT', ['days', self.reportdates[i]])
                Qgp = self.ecl.get_sim_results('FGPT', ['days', self.reportdates[i]])
                Qwp = self.ecl.get_sim_results('FWPT', ['days', self.reportdates[i]])
                Qwi = self.ecl.get_sim_results('FWIT', ['days', self.reportdates[i]])

            else:
                Qop = self.ecl.get_sim_results('FOPT', ['days', self.reportdates[i]]) - self.ecl.get_sim_results('FOPT', ['days', self.reportdates[i - 1]])
                Qgp = self.ecl.get_sim_results('FGPT', ['days', self.reportdates[i]]) - self.ecl.get_sim_results('FGPT', ['days', self.reportdates[i - 1]])
                Qwp = self.ecl.get_sim_results('FWPT', ['days', self.reportdates[i]]) - self.ecl.get_sim_results('FWPT', ['days', self.reportdates[i - 1]])
                Qwi = self.ecl.get_sim_results('FWIT', ['days', self.reportdates[i]]) - self.ecl.get_sim_results('FWIT', ['days', self.reportdates[i - 1]])

            val = (Qop * wop + Qgp * wgp - Qwp * wwp - Qwi * wwi) / ((1 + disc) ** (self.reportdates[i] / 365.25))
            initial_gh = np.append(initial_gh, val)

        #print("initial gh", initial_gh)

        # Get all remaining wells
        re_wells = new_state["name"][Ns:]

        producers = []
        injectors = []

        # Calculate economic indicator for each remaining wells
        for well in re_wells:
            val_well = []

            # Calculate economic value for producer "OP_"
            if "OP" in well:
                for i in range(len(self.reportdates)):
                    if i == 0:
                        Wopt = self.ecl.get_sim_results('WOPT ' + well, ['days', self.reportdates[i]])
                        Wwpt = self.ecl.get_sim_results('WWPT ' + well, ['days', self.reportdates[i]])
                        Wgpt = self.ecl.get_sim_results('WGPT ' + well, ['days', self.reportdates[i]])

                    else:
                        Wopt = self.ecl.get_sim_results('WOPT ' + well, ['days', self.reportdates[i]])-self.ecl.get_sim_results('WOPT ' + well, ['days', self.reportdates[i-1]])
                        Wwpt = self.ecl.get_sim_results('WWPT ' + well, ['days', self.reportdates[i]])-self.ecl.get_sim_results('WWPT ' + well, ['days', self.reportdates[i-1]])
                        Wgpt = self.ecl.get_sim_results('WGPT ' + well, ['days', self.reportdates[i]])-self.ecl.get_sim_results('WGPT ' + well, ['days', self.reportdates[i-1]])

                    val = (Wopt * wop + Wgpt * wgp - Wwpt * wwp) / ((1 + disc) ** (self.reportdates[i] / 365.25))
                    # val = random.random()
                    val_well = np.append(val_well, val)

                producers.append({'name': well, 'PWEI': sum(val_well)})
            else:
                # Calculate value for injector
                for i in range(len(self.reportdates)):
                    if i == 0:
                        Wwit = self.ecl.get_sim_results( 'WWIT ' + well, ['days', self.reportdates[i]])

                    else:
                        Wwit = self.ecl.get_sim_results('WWIT ' + well, ['days', self.reportdates[i]]) - self.ecl.get_sim_results('WWIT ' + well, ['days', self.reportdates[i - 1]])

                    val = (-Wwit * wwi) / ((1 + disc) **(self.reportdates[i] / 365.25))
                    # val = random.random()
                    val_well= np.append(val_well, val)

                injectors.append({'name': well, 'IWEI': sum(val_well)})

        # Rank producers and injectors
        producers = sorted(producers, key=lambda k: k['PWEI'])
        injectors = sorted(injectors, key=lambda k: k['IWEI'],reverse=True)

        ranked_producers = producers
        ranked_injectors = injectors

        """
        ranked_producers = []
        for element in producers:
            ranked_producers.append(element["name"])

        ranked_injectors = []
        for element in injectors:
            ranked_injectors.append(element["name"])
        """
        # Prior space reduction, keep half of the remaining wells as next action
        scale = 0.5
        prior_pro = producers[math.trunc(scale*len(producers)):]
        prior_inj = injectors[math.trunc(scale*len(injectors)):]
        prior_wells = prior_pro + prior_inj
        
        # return to the names of next possible wells after prior space reduction
        next_actions = []
        for element in prior_wells:
            next_actions.append(element["name"])

        return initial_gh, ranked_producers, ranked_injectors, next_actions

    def get_initialvalue(self, initial_gh, Nw, Ns):

        """
        Get initial estimated values of various time periods
        Input:
            initial_gh:    initial estimated value of each time period
            Nw:             Number of all wells
            Ns:             Number of selected wells
        Output:
            return_argvs:   initial estimated values of various time periods
        """

        g = initial_gh[:Ns]
        hr = initial_gh[Ns: Nw - 1]
        hs = initial_gh[Nw - 1:]
        total_g = sum(g)
        initial_hr = sum(hr)
        total_ghr = total_g + initial_hr   
        initial_hs = sum(hs)  
        original_npv = sum(initial_gh)


        total_g = float("%.6f" % total_g)
        initial_hr = float("%.6f" % initial_hr)
        total_ghr = float("%.6f" % total_ghr)
        initial_hs = float("%.6f" % initial_hs)
        original_npv = float("%.6f" % original_npv)
        g = [float("%.6f" % it) for it in g]
        hr = [float("%.6f" % it) for it in hr]
        hs = [float("%.6f" % it) for it in hs]

        return_argvs = {
            'g': g,
            'hr': hr,
            'hs': hs,
            'total_g': total_g,
            'initial_hr': initial_hr,
            'total_ghr': total_ghr,
            'initial_hs': initial_hs,
            'original_npv': original_npv,
        }
        return return_argvs

    #####     end for get initial   ##########

    def get_initial_data(self, new_state, Ns):
        Nw = len(new_state['name'])

        initial_gh, ranked_producers, ranked_injectors, next_actions = self.get_initial_gh(new_state, Nw, Ns)
        # initial_gh = [random.random() for x in range(10)]
        initial_gh = [float("%.6f" % it) for it in initial_gh]
        initial_data = self.get_initialvalue(initial_gh, Nw, Ns)
        return initial_data, ranked_producers, ranked_injectors, next_actions
        # return initial_data, ['OP_1', 'OP_2', 'OP_3']
