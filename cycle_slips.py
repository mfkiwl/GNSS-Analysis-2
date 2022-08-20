from constants import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime


class observables(object):
    
    def __init__(self, df, prn = None):
        
        self.df = df 
        self.prns = np.unique(self.df.index.get_level_values('sv').values)
        
        if prn is not None:
            obs = self.df.loc[self.df.index.get_level_values('sv') == prn, :]
        else:
            obs = self.df
    
        self.l1 = obs.L1.values
        self.l2 = obs.L2.values
        self.c1 = obs.C1.values
        self.p2 = obs.P2.values
        
        self.l1lli = obs.L1lli.values.astype(int)
        self.l2lli = obs.L2lli.values.astype(int)
        
        self.time = pd.to_datetime(obs.index.get_level_values('time'))
        
        
def correct_phases(RTEC, MWLC, l1, l2, c1, p2, index):
    diff_tec = RTEC[index - 1] - RTEC[index]
    diff_mwlc = MWLC[index - 1] - MWLC[index]
    
    diff_2 = round(diff_tec - (diff_mwlc * const.c / const.F1) 
                   * const.factor_2)
    
    diff_1 = diff_2 + round(diff_mwlc)
    
    corr_1 = l1[index] - diff_1
    corr_2 = l2[index] - diff_2
    
    RTEC[index] = ((corr_1 / const.F1) - (corr_2 / const.F2)) * const.c
    MWLC[index] = ((corr_1 - corr_2) - (const.F1 * c1[index] + 
                                        const.F2 * p2[index]) * const.factor_1)
    
    for num in range(index, len(l1)):
        
        l1[num] = l1[num] - diff_1
        l2[num] = l2[num] - diff_2
        
    return l1, l2