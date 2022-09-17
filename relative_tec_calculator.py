from constants import constants as const
from cycle_slips import cycle_slip_corrector
from build import paths
import pandas as pd
import datetime
from load import load_receiver


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

def relative_tec_data(df, prn: str = "G01") -> pd.DataFrame:
    
    """
    Read pre-process files (already missing values removed), 
    correct cycle-slip and compute the relative tec (in TECU)
    """

    time, c1_values, p2_values, rtec = cycle_slip_corrector(df, prn)
    
    stec = relative_tec(time, c1_values, p2_values, rtec, prn)
    
    df = pd.DataFrame({prn: stec}, index = time)
    
    date = df.index[0]
    
    year, month, day = date.year, date.month, date.day
    
    str_date = f"{year}-{month}-{day}"
    
    index  = pd.date_range(start = str_date + " 00:00:00", 
                           end = str_date + " 23:59:45", 
                           freq = "15s")
    df = df.reindex(index)
    df.index.name = "time"
    return df
    
 
def main():
    
    year = 2014
    doy = 1
    path = paths(year, doy)
    station = "alar"
    infile = path.fn_rinex(station)
     
    df = load_receiver(infile).df
    prn = "G01" 
    df = relative_tec_data(df, prn = prn)
    
    print(df)
    
    df.plot()
    
#main()
    

