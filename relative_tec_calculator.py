
from constants import constants as const
from load import *
from cycle_slips import *



def relative_tec(time, c1, p2, rtec):
    
    """
    Calculo do TEC relativo a partir das pseudodistâncias
    Relative TEC (rTEC) from the pseudoranges
    """
    
    narc = 1
    index_last = 0

    # Diferença entre as pseudodistâncias    
    a1 = p2[0] - c1[0]
    b = rtec[0] - a1
    
    
    for index in range(1, len(time)):
        
        if (time[index] - time[index - 1] > datetime.timedelta(minutes = 15)):
            
            b = b / narc
            
            for elem in range(index_last, index):
                rtec[elem] = const.factor_TEC * (rtec[elem] - b)
            
            index_last = index
            narc = 1
            a1 = p2[index] - c1[index]
            
            b = rtec[index] - a1
            
        else:
            narc += 1
            a1 = p2[index] - c1[index]
            b = b + (rtec[index] - a1)
            
    b = b / narc
    
    for elem in range(index_last, len(time)):
    
        rtec[elem] = const.factor_TEC * (rtec[elem] - b)
        
    return rtec

def main():
    
    filename = "alar0011.14o"

    df = pd.read_csv(f"Database/{filename}.txt", 
                     delim_whitespace=(True), 
                     index_col = ["sv", "time"])


    prn = "G01"
    ob = observables(df, prn = prn)

    # phases carriers
    l1_values = ob.l1
    l2_values = ob.l2

    # Loss Lock Indicator (lli)
    l1lli_values, l2lli_values = ob.l1lli, ob.l2lli

    # Pseudoranges
    c1_values, p2_values = ob.c1, ob.p2

    # time
    time = ob.time

    

    l1, l2, rtec = cycle_slip_corrector(time, l1_values, l2_values, 
                                        c1_values, p2_values, 
                                        l1lli_values, l2lli_values)
    
    
    rtec = relative_tec(time, c1_values, 
                        p2_values, rtec)
   
    print(rtec)
    
    
    
