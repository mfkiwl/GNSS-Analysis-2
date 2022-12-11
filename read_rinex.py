import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def get_header(infile):
    lines = open(infile, "r").readlines()
    dict_infos = {}
    
    for line in lines:
        
        if "END OF HEADER" in line:
            break
        else:
                    
            info_obj = _remove_values(line[:60].split("   "))
           
            info_type = line[60:].title().replace(" ", "").replace("\n", "")
            
            dict_infos[info_type] = _remove_values(info_obj)

            
    return dict_infos


def _split_prns(epoch):
    prns_list = []
    for prns in epoch:
    
        prns_list.append([prns[2:][y - 3: y] for y in 
                          range(3, len(prns[2:]) + 3, 3)])        
    return prns_list


def _replace_values(list_to_replace, 
                   item_to_replace = "", 
                   item_to_replace_with = np.nan):
    
    return [item_to_replace_with if item == item_to_replace 
            else item for item in list_to_replace]


def _remove_values(list_to_remove, item_to_remove = ""):
    return [item.strip() for item in list_to_remove if item != ""]


def _times(infile):

    attrs = get_header(infile)
    
    first_obs = attrs['TimeOfFirstObs']
    interval = attrs["Interval"][0][:2]
    
    year = int(first_obs[0])
    month = int(first_obs[1])
    day = int(first_obs[2])
    
    hour = int(first_obs[3])
    minute = int(first_obs[4])
    sec = int(float(first_obs[5]))
    
    
    start = datetime(year, month, day, 
                    hour, minute, sec)

    end = start + timedelta(hours = 23, 
                            minutes = 59, 
                            seconds = 45)

    return pd.date_range(start, end, freq = f"{interval}s")

def _get_data_for_each_epoch(elem, prns_list, time):
    
    columns = []
    
    for j in range(len(elem)):
            
        elemlist = elem[j].lstrip().replace("\n", "")
        
        L1 = elemlist[0:13].strip()
        L1lli = elemlist[13:14].strip()
        #L1ssi = elemlist[14:15].strip()
        C1 = elemlist[17:29].strip()
        #C1ssi = elemlist[30:31].strip()
        L2 = elemlist[32:45].strip()
        L2lli = elemlist[45:46].strip()
        P2 = elemlist[47:61].strip()
        #L2ssi = elemlist[61:62].strip()
        #P2ssi = elemlist[62:63].strip()
        
        observables = [time, prns_list[j], L1, L1lli,
                       C1, L2, L2lli, P2]
       #lock_indicator = [ ]
        columns.append(_replace_values(observables))    
        
    return columns

def _get_prns_rows(lines):
    
    epoch = []
    indexes = []
    
    for i in range(15, len(lines)):
        
        current = lines[i]
                    
        if any([i in current 
                for i in ["G", "R"]]):
            epoch.append(current.strip())
            indexes.append(i)
    return epoch, indexes


def _get_epochs(lines):
    
    epoch, indexes = _get_prns_rows(lines)
    
    epoch_fix = []
    indexes_fix = []
    for i in range(0, len(epoch) - 1, 2):
        
        res = (epoch[i] + epoch[i + 1]).split("  ")
        
        epoch_fix.append(res[-1][2:])
        indexes_fix.append(indexes[i])
    
    return _split_prns(epoch_fix), indexes_fix


def _get_rows_for_each_time(infile):
    
    lines = open(infile, "r").readlines()
    epoch, indexes = _get_epochs(lines)
    times =  _times(infile)
    
    result = []
  
    for num in range(0, len(indexes)):
        
        prns_list = epoch[num]
        time = times[num]
        
        if num == len(indexes) - 2:
            start = indexes[-2] + 2
            end = indexes[-1]
        elif num == len(indexes) - 1:
            start = indexes[-1] + 2
            end = None
        else:
            start = indexes[num] + 2
            end = indexes[num + 1]
            
        
        elem = lines[start: end]
        
        
        result.extend(_get_data_for_each_epoch(elem, 
                                               prns_list, 
                                               time))

    cols = ["time", "prn", "L1", "L1lli", "C1", 
            "L2", "L2lli", "P2"]

    return pd.DataFrame(result, columns = cols)



def main():
    infile = "database/rinex/2014/alar0011.14o"
    
    df = _get_rows_for_each_time(infile)
    print(df)

main()