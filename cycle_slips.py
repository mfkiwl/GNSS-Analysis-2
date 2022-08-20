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
        
        
def correct_phases(RTEC, MWLC, 
                   l1_values, l2_values, 
                   c1_values, p2_values, i):
    
    const = constants()
    
    l1 = l1_values[i]
    l2 = l2_values[i]
    c1 = c1_values[i]
    p2 = p2_values[i]
    
    diff_tec = RTEC[i] - RTEC[i - 1]
    diff_mwlc = MWLC[i] - MWLC[i - 1]
    
    diff_2 = np.round((diff_tec - (diff_mwlc * const.c 
                                   / const.F1)) * const.factor_mw)
    
    
    diff_1 = diff_2 + np.round(diff_mwlc)
    
    corr_1 = l1 - diff_1
    corr_2 = l2 - diff_2
    
    RTEC[i] = ((corr_1 / const.F1) - (corr_2 / const.F2)) * const.c
    MWLC[i] = ((corr_1 - corr_2) - (const.F1 * c1 + const.F2 * p2) * const.factor)
    
    for num in range(i, len(l1_values)):
        
        l1_values[num] = l1_values[num] - diff_1
        l2_values[num] = l2_values[num] - diff_2
        
    return l1_values, l2_values


def cycle_slip_corrector(time, l1_values, l2_values, 
                         c1_values, p2_values, 
                         l1lli_values, l2lli_values):
    
  
    const = constants()
    index_start = 0
    size = 10
    
    
    RTEC = np.zeros(len(time)) # TEC relativo
    MWLC = np.zeros(len(time)) # Combinação linear Melbourne–Wübbena
    
    
    for index in range(0, len(time)):
        
        l1 = l1_values[index]
        l2 = l2_values[index]
        c1 = c1_values[index]
        p2 = p2_values[index]
        
        
        RTEC[index] = ((l1 / const.F1) - (l2 /  const.F2)) * const.c
        
        # Compute the Melbourne-Wubbena
        MWLC[index] = ((l1 - l2) - (const.F1 * c1 +  const.F2 * p2) * const.factor)
        

        # Se encontrar o gap comece o index_start
        
        if (time[index] - time[index - 1] > datetime.timedelta(minutes = 15)):
            index_start = index
            
            #continue # Essa condição talvez esteja compromentando o segundo loop
        l_slip1 = l1lli_values[index] % 2
        l_slip2 = l2lli_values[index] % 2
        
        # Verifique se o resto do lli é igual a 1
        if (l_slip1 == 1 or l_slip2 == 1):
            
            l1_values, l2_values = correct_phases(RTEC, MWLC, 
                                                  l1_values, l2_values, 
                                                  c1_values, p2_values, index)
            
        pmean = 0.0
        pdev = const.DIFF_TEC_MAX * 4.0
        
        if index - index_start + 1 >= 12:
            
            add_tec = 0
            add_tec_2 = 0
            
            for elem in range(1, size):
                add_tec = add_tec + RTEC[index - elem] - RTEC[index - 1 - elem]
                
                add_tec_2 = add_tec_2 + np.power(RTEC[index - elem] -  
                                            RTEC[index - 1 - elem], 2)
                
            pmean = add_tec / size
            
            pdev = max(np.sqrt(add_tec_2 / size - np.power(pmean, 2)), 
                       const.DIFF_TEC_MAX)
            
        pmin_tec = pmean - pdev * 5.0
        pmax_tec = pmean + pdev * 5.0
        
        diff_tec = RTEC[index] - RTEC[index - 1]
        
        if not (pmin_tec <= diff_tec < pmax_tec):
            
            l1_values, l2_values = correct_phases(RTEC, MWLC, 
                                                  l1_values, l2_values, 
                                                  c1_values, p2_values, index)

            
    return l1_values, l2_values, RTEC