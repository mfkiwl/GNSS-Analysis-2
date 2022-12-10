
from datetime import datetime

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

    return datetime(year, month, day, 
                    hour, minute, sec)


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

epoch, indexes = get_epoch(lines)
prns_list = get_prns(epoch)