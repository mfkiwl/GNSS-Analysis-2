from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def find_gaps(time, gap_delta = 15):
    
    df = pd.DataFrame(time.values, columns = ['times'])

    df["deltas"] = df['times'].diff()[1:]

    df["check_gap"] = np.where(df.deltas > 
                               timedelta(seconds = 2 * gap_delta), True, False)

    df["count_gaps"] = df["check_gap"].cumsum()

    index_of_gaps = [df.loc[df["count_gaps"] == num, :].index for 
                     num in np.unique(df['count_gaps'])]

    return index_of_gaps


def rot_func(stec, time, length = 1):

    delta_tec = (np.roll(stec, -1) - stec)
    delta_time = np.array((np.roll(time, -1) - time).astype('timedelta64[s]')).astype('float64')
    
    step_range = slice(length, len(delta_tec) - length)
    
    rot_vals = (delta_tec[step_range] / (delta_time[step_range]))*60.
    
    return rot_vals

def running(x, N):
    return np.convolve(x, np.ones(N)/N, mode='same')

def rot(stec, time, length = 1, gap_delta = 15, N = 10):
    
    """Rate of TEC"""
    
    gaps = find_gaps(time, 
                     gap_delta = gap_delta)
    
    rot_out = []
    time_out = []
    
    for num in range(len(gaps)):
        
   
        t = time[gaps[num]]
        s = stec[gaps[num]]
        
        
        delta_tec = (np.roll(s, -1) - s)
        delta_time = np.array((np.roll(t, -1) - t).astype('timedelta64[s]')).astype('float64')
    
        step_range = slice(length, len(delta_tec) - length)
    
        nt = t[length: len(t) - length]

        rot_out.extend((delta_tec[step_range] / (delta_time[step_range]))*60.)
        time_out.extend(nt)
        
    if N:
        rot = running(rot_out, N) -  rot_out
    else:
        rot = rot_out
    return time_out, rot



def roti(stec, time, step = 4, length = 1):
    """Rate of TEC Index"""
    dtime = [(i.hour + i.minute/60. + i.second/(3600.)) 
                    for i in time]

    out_roti = []
    out_time = []

    rtime, rot_1 = rot(stec, time, length = 1)
    
    
    for j in range(step, len(rot_1) - step, step):

        avg_of_power = np.mean(np.power(rot_1[j - step: j + step], 2))
        power_of_avg = np.power(np.mean(rot_1[j - step: j + step]), 2)

        out_time.append(rtime[j])
        
        out_roti.append(np.sqrt(avg_of_power - power_of_avg))

    return out_time, out_roti
