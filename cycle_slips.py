# -*- coding: utf-8 -*-
"""
Created on Fri Aug 12 10:16:07 2022

@author: Luiz
"""

c = 299792458.0
DIFF_TEC_MAX = 0.05

TEC_U = 10000000000000000.0  # 10e15


import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt

def LLI(x):
    lli = str(x).split(".")[1]
    
    return int(lli)
  
df = pd.read_csv("Database/process.txt", 
                 delim_whitespace = True,
                 index_col=["time", "sv", "ECEF"])


PRN = list(df.index.levels[1])

measures = df.loc[((df.index.get_level_values(1) == PRN[0]) &
              (df.index.get_level_values(2) == "x")), :]

measures.index = pd.to_datetime(measures.index.get_level_values(0))


# Time values in datetime format
time = pd.to_datetime(measures.index.values) 

# Phase measurements
phase_1 = measures.L1.values 
phase_2 = measures.L2.values

# Loss of Lock Indicator (LLI) measurements
phase_1_lli = np.array(list(map(LLI, phase_1)))
phase_2_lli = np.array(list(map(LLI, phase_2)))

# Psedorange measurements
pseudo_1 = measures.C1.values
pseudo_2 = measures.P2.values

def update(mwlc: np.array, 
            phase1: np.array, 
            phase2: np.array, 
            pseudo1: np.array, 
            pseudo2: np.array,
            RTEC: np.array, 
            index: int, 
            f1:float, 
            f2: float, 
            c: float) -> tuple:
    
    """
    RTEC = Relative TEC; 
    f1 = Primary frequency; 
    f2 =  Secundary frequency
    c = speed light
    """

    l1 = phase1[index]
    l2 = phase2[index]
    c1 = pseudo1[index]
    p2 = pseudo2[index]
    
    # Calcule alguns fatores 
    factor1 = (f1 - f2) / (f1 + f2) / c
    factor2 = (f1 * f2) / (f2 - f1) / c

    diff_tec = RTEC[index] - RTEC[index - 1]
    diff_mwlc = mwlc[index] - mwlc[index - 1]

    diff_2 = np.round((diff_tec - (diff_mwlc * c / f1)) * factor2)
    diff_1 = diff_2 + np.round(diff_mwlc)

    corr_1 = l1 - diff_1
    corr_2 = l2 - diff_2

    RTEC[index] = ((corr_1 / f1) - (corr_2 / f2)) * c
    mwlc[index] = (corr_1 - corr_2) - (f1 * c1 + f2 * p2) * factor1

    for k in range(index, len(phase1)):
        phase1[k] = phase1[k] - diff_1
        phase2[k] = phase2[k] - diff_2

    return phase1, phase2

def detect_gap(d_inicial: datetime.datetime, 
               d_final: datetime.datetime) -> bool:
    
    ARC_GAP_TIME = 0.01
    
    
    def datetime_to_float(hour: int, 
                          minute: int, 
                          second:int):
        
        return ((hour / 24.0) + 
                (minute / 1440.0) + 
                (second / 86400.0))
        
    
    t1 = datetime_to_float(d_inicial.hour, 
                           d_inicial.minute, 
                           d_inicial.second)

     
    t2 = datetime_to_float(d_final.hour, 
                           d_final.minute, 
                           d_final.second)

    return t2 - t1 > ARC_GAP_TIME

f1 = 1575.42e6 
f2 = 1227.60e6

RTEC = np.zeros(len(time))
mwlc = np.zeros(len(time))

j_start = 0 

out = []

for j in range(0, 5):
    l1 = phase_1[j]
    l2 = phase_2[j]
    c1 = pseudo_1[j]
    p2 = pseudo_2[j]
    
    factor2 = ((f1 - f2) / (f1 + f2) / c)
    
    RTEC[j] = ((l1 / f1) - (l2 / f2)) * c
    
    mwlc[j] = (l1 - l2) - (f1 * c1 + f2 * p2) * factor2
    
    print(RTEC[j])
    
    if j > 0:

        has_gap = detect_gap(time[j - 1], time[j])
        
        if has_gap:
            j_start = j
            
            

        aux_l1 = phase_1_lli[j]
        aux_l2 = phase_2_lli[j]
        print(aux_l1)
        aux_l1 = 0 if np.isnan(aux_l1) else int(aux_l1)
        aux_l2 = 0 if np.isnan(aux_l2) else int(aux_l2)
        l_slip1 = aux_l1 % 2
        l_slip2 = aux_l2 % 2
        
        if (l_slip1 == 1 or l_slip2 == 1):
            
            
           phase_1, phase_2 = update(mwlc, phase_1,
                                     phase_2, pseudo_1,
                                     pseudo_2, RTEC, j,
                                     f1, f2, c)
       


