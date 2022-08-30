import pandas as pd
from scipy import stats
import numpy as np



def time_gap(time, tgap = None):

   


    ts = pd.DataFrame({"time": time})
    ts['Timedelta'] = ts['time'].diff()
    ts['second_delta'] = ts['Timedelta'].astype('timedelta64[s]')
    mode = stats.mode(ts['Timedelta'].astype('timedelta64[s]'))


    if tgap == None:
        ts['newSession'] = np.where(ts['second_delta'] > 2 * mode[0][0], True, False)
    else:
        ts['newSession'] = np.where(ts['second_delta'] > tgap, True, False)

    ts['SessionID'] = ts['newSession'].cumsum()
    vls, cnts = np.unique(ts['SessionID'], return_counts = True)    

    delta_hora = ts['second_delta']

    id_dict = {}
    for i in range(len(vls)):        
        id_dict[vls[i]] = ts.index[ts['SessionID'] == vls[i].tolist()]
        
    return vls, cnts, id_dict, mode, delta_hora
    
def Rate_TEC(stec, time):
    
    vls, cnts, id_dict, mode, delta_hora = time_gap(time)
    
    decimal_time = [(i.hour + i.minute/60. +i.second/(3600.)) for i in time]
    
    
    if mode[0] == 1: 
        step_hora = 60
    elif mode[0] == 15:
        step_hora = 4
    elif mode[0] == 30:
        step_hora = 2


    rot = []
    roti = []
    rot_tstamps = []
    roti_tstamps = []
    for i in range(len(vls)): 


        delta_time = decimal_time[id_dict[i][-1]] - decimal_time[id_dict[i][0]]     

        deltahora = [delta_hora[k] for k in id_dict[i]]    
        t_temp = [time[k] for k in id_dict[i]]                     
        stec_temp = [stec[k] for k in id_dict[i]]

        shift_stec = np.roll(stec_temp, -1)
        rot_0 = (shift_stec - stec_temp)
        rot_1 = (rot_0[1:len(rot_0) - 1] / (deltahora[1:len(rot_0)-1]))*60.
        rot.extend(rot_1)
        rot_tstamps.extend(t_temp[1:len(t_temp)-1])

        if float(delta_time) >= 0.166667:                

            for j in range(step_hora, len(rot_1) - step_hora, step_hora):
                rot_2 = np.sqrt(np.mean(np.power(rot_1[j - step_hora:j + step_hora], 2)) - 
                                np.power(np.mean(rot_1[j - step_hora:j + step_hora]), 2))
                roti.append(rot_2)
                roti_tstamps.append(t_temp[j])
                
    return rot, rot_tstamps, roti, roti_tstamps