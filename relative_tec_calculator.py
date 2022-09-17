from constants import constants as const
from cycle_slips import cycle_slip_corrector
from build import build_paths
import pandas as pd
import datetime



def relative_tec(time, c1, p2, rtec, prn):
    
    """Compute the Relative TEC (slant) from the pseudoranges"""
    
    narc = 1
    index_last = 0

    # Diferença entre as pseudodistâncias    
    a1 = p2[0] - c1[0]
    b = rtec[0] - a1
    
    
    for index in range(1, len(time)):
        
        if (time[index] - time[index - 1] > 
            datetime.timedelta(minutes = 15)):
            
            b = b / narc
            
            for elem in range(index_last, index):
                rtec[elem] = const.factor_TEC(prn) * (rtec[elem] - b)
            
            index_last = index
            a1 = p2[index] - c1[index]
            
            b = rtec[index] - a1
            
        else:
            narc += 1
            a1 = p2[index] - c1[index]
            b = b + (rtec[index] - a1)
            
    b = b / narc
    
    for elem in range(index_last, len(time)):
    
        rtec[elem] = const.factor_TEC(prn) * (rtec[elem] - b)
        
    return rtec

def relative_tec_data(infile: str, prn: str = "G01") -> pd.DataFrame:
    
    """
    Read pre-process files (already missing values removed), 
    correct cycle-slip and compute the relative tec (in TECU)
    """
    
    df = pd.read_csv(infile, delim_whitespace = True, index_col = ["sv", "time"])

    time, c1_values, p2_values, rtec = cycle_slip_corrector(df, prn)
    
    stec = relative_tec(time, c1_values, p2_values, rtec, prn)

    return pd.DataFrame({"stec": stec}, index = time)
    
    
def main():
    
    year = 2014
    doy = 1
    
    infile = build_paths(year, doy).fn_process("alar001")
    
    prn = "R01" 
    df = relative_tec_data(infile, prn = prn)
    
    import matplotlib.pyplot as plt
    
    df.plot()
    
    
main()
    

