import read_rinex as r
from constants import constants as c
import matplotlib.pyplot as plt
import numpy as np
from datetime import timedelta, datetime



def RTEC(l1, l2, f1, f2):
    """Compute relative from phases"""
    return ((l1 / f1) - (l2 /  f2)) * c.c

def wl_wavelength(f1, f2):
    """wide-lane wavelength. For GPS ~82cm"""
    return c.c / (f1 - f2)

def factor_nw(f1, f2):
    return (f1 * f2) / (f2 - f1) / c.c

def MWWL(l1, l2, c1, p2, f1, f2):
    """Compute Melbourne–Wübbena linear combination"""
    lambda_factor = wl_wavelength(f1, f2) * (f1 + f2)
    return (l1 - l2) - (f1 * c1 + f2 * p2) / lambda_factor


def correct(l1, l2, c1, p2, 
            rtec, l, i, f1, f2):
    
    """Use the MW ambiguity for to correct the phases lost"""
        
    diff_tec = rtec[i] - rtec[i - 1]
    
    diff_mwlc = l[i] - l[i - 1]
            
    diff_2 = (diff_tec - (diff_mwlc * c.c / f1)) * factor_nw(f1, f2)
    
    # Sem aplicar o 'round' a correção, aparentemente, apresenta um 
    # comportamento melhor
    diff_1 = diff_2 + diff_mwlc
    
    # correção das fases 1 e 2 na epoca em que o cycle splip ocorreu 
    corr_1 = l1[i] - diff_1
    corr_2 = l2[i] - diff_2
    
    # Correção do rtec no ponto de perda de fase
    rtec[i] = RTEC(corr_1, corr_2, f1, f2) 
    
    # correção de todas epocas subsequentes
    l1[i: len(l1)] -= diff_1
    l2[i: len(l2)] -= diff_2
    return l1, l2


def deviations(i, 
               i_start, 
               rtec, 
               diff_tec_max = 0.05, 
               size = 10):
               
     if i - i_start + 1 >= 12:
        
         add_tec = 0
         add_tec_2 = 0
        
         for j in range(1, size):
             add_tec += rtec[i - j] - rtec[i - 1 - j]
             add_tec_2 += pow(rtec[i - j] -  rtec[i - 1 - j], 2)
            
         pmean = add_tec / size
         chunk_pdev = np.sqrt(add_tec_2 / size - pow(pmean, 2))
         pdev = max(chunk_pdev, diff_tec_max)
     else:
         pmean = 0
         pdev = diff_tec_max * 2.5
        
     pmin_tec = pmean - pdev * 2
     pmax_tec = pmean + pdev * 2
    
     return pmin_tec, pmax_tec
 
    
def CycleSlip(l1, l2, c1, p2, prn, 
              time, l1lli, l2lli, 
              f1, f2):
    
    tec = np.zeros(len(time)) # TEC relativo
    nwl = np.zeros(len(time)) # Combinação linear Melbourne–Wübbena
    
    i_start = 0
    
    for i, epoch in enumerate(time):
         
        tec[i] = RTEC(l1[i], l2[i], f1, f2)
        
        nwl[i] = MWWL(l1[i], l2[i], c1[i], p2[i], f1, f2)
        
        # Verifique se o último bit do lli
        l_slip1 = l1lli[i] % 2
        l_slip2 = l2lli[i] % 2
            
        # Verifique se o resto do lli é igual a 1
        if (l_slip1 == 1 or l_slip2 == 1):
    
            l1, l2 = correct(l1, l2, c1, p2, 
                             tec, nwl, i, f1, f2)
        
        if (time[i] - time[i - 1]) > timedelta(minutes = 15):
            i_start = i
            continue
 
        pmin, pmax = deviations(i, i_start, tec)
    
        diff_tec = tec[i] - tec[i - 1]
        
        if not (pmin <= diff_tec < pmax):
            
            l1, l2 = correct(l1, l2, c1, p2, 
                             tec, nwl, i, f1, f2)
    return tec
            

def plot(time, rtec):
    
    fig, ax = plt.subplots()
    ax.plot(time, rtec, label = "RTEC corrigido")
    ax.legend()
    
    ax.set(ylabel = "TEC relativo", xlabel = "tempo")

def main():
    
    infile = "database/rinex/2014/alar0011.14o"

    prn = "G01"
            
    df = r.load_rinex(infile, prn, False, False)

    time = df.time
    l1 = df.l1
    l2 = df.l2
    c1 = df.c1
    p2 = df.p2
    f1 = df.F1
    f2 = df.F2
    l1lli = df.l1lli
    l2lli = df.l2lli
    
    rtec = CycleSlip(l1, l2, c1, p2, prn, 
                     time, l1lli, l2lli, 
                     f1, f2)
    
    plot(time, rtec)
    
    

