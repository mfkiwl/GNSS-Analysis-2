from constants import constants as const
import datetime
import numpy as np
from load import observables
import pandas as pd
from build import build_paths


def correct_phases(RTEC, MWLC, 
                   l1_values, l2_values, 
                   c1_values, p2_values, 
                   i, prn):
    
    F1, F2 = const.frequency(prn)
    
    
    l1 = l1_values[i]
    l2 = l2_values[i]
    c1 = c1_values[i]
    p2 = p2_values[i]
    
    diff_tec = RTEC[i] - RTEC[i - 1]
    diff_mwlc = MWLC[i] - MWLC[i - 1]
    
    diff_2 = np.round((diff_tec - (diff_mwlc * const.c / F1)) * const.factor_mw(prn))
    
    diff_1 = diff_2 + np.round(diff_mwlc)
    
    corr_1 = l1 - diff_1
    corr_2 = l2 - diff_2
    
    RTEC[i] = ((corr_1 / F1) - (corr_2 / F2)) * const.c
    MWLC[i] = ((corr_1 - corr_2) - (F1 * c1 + F2 * p2) * const.factor(prn))
    
    for num in range(i, len(l1_values)):
        
        l1_values[num] = l1_values[num] - diff_1
        l2_values[num] = l2_values[num] - diff_2
        
    return l1_values, l2_values


def cycle_slip_corrector(df, prn, DIFF_TEC_MAX = 0.05, size = 10) -> tuple:
    
    """Cycle slip correction for each prn"""
    ob = observables(df, prn = prn)

    # phases carriers (Fase das portadoras)
    l1_values = ob.l1
    l2_values = ob.l2

    # Loss Lock Indicator
    l1lli_values, l2lli_values = ob.l1lli, ob.l2lli

    # Pseudoranges (pseudistancias)
    c1_values, p2_values = ob.c1, ob.p2

    # tempo
    time = ob.time
    
    index_start = 0
    
    F1, F2 = const.frequency(prn)
    
    RTEC = np.zeros(len(time)) # TEC relativo
    MWLC = np.zeros(len(time)) # Combinação linear Melbourne–Wübbena
    
    
    for index in range(len(time)):
        
        l1 = l1_values[index]
        l2 = l2_values[index]
        c1 = c1_values[index]
        p2 = p2_values[index]
        
        # Calcule o TEC relativo a partir das fases
        RTEC[index] = ((l1 / F1) - (l2 /  F2)) * const.c
        
        # Compute the Melbourne-Wubbena
        MWLC[index] = ((l1 - l2) - (F1 * c1 + F2 * p2) * const.factor(prn))
        
        # Se encontrar o gap de 15 minutos inicie o "index_start"
        
        if (time[index] - time[index - 1] > datetime.timedelta(minutes = 15)):
            index_start = index
            
        # Encontre o resto das phase de bloqueio
        l_slip1 = l1lli_values[index] % 2
        l_slip2 = l2lli_values[index] % 2
        
        # Verifique se o resto do lli é igual a 1
        if (l_slip1 == 1 or l_slip2 == 1):
            
            l1_values, l2_values = correct_phases(RTEC, MWLC, 
                                                  l1_values, l2_values, 
                                                  c1_values, p2_values, 
                                                  index, prn)
        pmean = 0.0
        pdev = DIFF_TEC_MAX * 4.0
        
        if index - index_start + 1 >= 12:
            
            add_tec = 0
            add_tec_2 = 0
            
            for elem in range(1, size):
                add_tec = add_tec + RTEC[index - elem] - RTEC[index - 1 - elem]
                
                add_tec_2 = add_tec_2 + np.power(RTEC[index - elem] -  
                                            RTEC[index - 1 - elem], 2)
                
            pmean = add_tec / size
            
            pdev = max(np.sqrt(add_tec_2 / size - np.power(pmean, 2)), 
                       DIFF_TEC_MAX)
            
        pmin_tec = pmean - pdev * 5.0
        pmax_tec = pmean + pdev * 5.0
        
        diff_tec = RTEC[index] - RTEC[index - 1]
        
        if not (pmin_tec <= diff_tec < pmax_tec):
            
            l1_values, l2_values = correct_phases(RTEC, MWLC, 
                                                  l1_values, l2_values, 
                                                  c1_values, p2_values, 
                                                  index, prn)

            
    return time, c1_values, p2_values, RTEC



def main():
    
    station = "alar001"
    year = 2014
    doy = 1
    
    path = build_paths(year, doy).fn_process(station)

    df = pd.read_csv(path, delim_whitespace = True, index_col = ["sv", "time"])
    
    arr = np.array(df.index.get_level_values("sv"))
    
    #print(np.unique(arr))
    prn = "G02"
    
    time, c1, p2, rtec = cycle_slip_corrector(df, prn)
    
    print(rtec)
    
main()