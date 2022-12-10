import pandas as pd
import numpy as np
from datetime import datetime, timedelta

infile = "database/rinex/2014/alar0011.14o"

def get_header(infile):

    lines = open(infile, "r").readlines()
    
    header = []
    
    for line in lines:
        
        if "END OF HEADER" in line:
            break
        else:
            header.append(line.strip())
            
    return header 

def attributes(infile):
    
    header = get_header(infile)
    
    dict_infos = {}
    
    for num in range(len(header)):
        elements = header[num].split("    ")
        
        info_type = elements[-1].replace(" ", "")
        
        info_obj = [i for i in elements[:-1] if i != ""]
    
        dict_infos[info_type] = info_obj
    
    
    return dict_infos


def start_datetime(infile):

    attrs = attributes(infile)
    
    first_obs = attrs['TIMEOFFIRSTOBS']
    
    
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

    return pd.date_range(start, end, freq = "15s")

lines = open(infile, "r").readlines()


def get_epoch(lines):
    epoch = []
    indexes = []
    for i in range(15, len(lines)):
        current = lines[i]
        if len(current) == 69:
            
            res = (lines[i].replace("\n", "") + 
                            lines[i + 1].replace("\n", "").strip())
                            
            epoch.append(res.split("  ")[-1][2:])
            indexes.append(i)
            
    return epoch, indexes
        
def get_prns(epoch):
    prns_list = []
    for prns in epoch:
    
        prns_list.append([prns[2:][y - 3: y] for y in 
                          range(3, len(prns[2:]) + 3, 3)])        
    return prns_list




    rows = []
    for i in elem_list:
        observable = float(i[:-2])
        lockphase = i[-2:-1]
        if lockphase == " ":
            lockphase = np.nan
        else:
            lockphase = int(i[-2:-1])
        rows.append(observable)
        rows.append(lockphase)
        
    return rows
num = 0


def get_rows(elem_list):
    epoch, indexes = get_epoch(lines)
    elem = lines[indexes[num] + 2: indexes[num + 1]]
    
    prns_list = get_prns(epoch)

    
    sv = prns_list[num]
    columns = []
    for j in range(len(elem)):
            
        elemlist = elem[j].lstrip().replace("\n", "")
        
        L1 = elemlist[0:13]
        L1lli = elemlist[13:14]
        L1ssi = elemlist[14:15]
        C1 = elemlist[17:29]
        C1ssi = elemlist[30:31]
        L2 = elemlist[32:45].strip()
        L2lli = elemlist[45:46]
        P2 = elemlist[47:61]
        L2ssi = elemlist[61:62]
        P2ssi = elemlist[62:63]
        
        columns.append([sv[j], L1, L1lli, C1, L2, L2lli, P2])    
        
    print(columns)
