from read_rinex import _remove_values, _replace_values
import numpy as np

infile = "database/rinex/ALMA00BRA_R_20182440000_01D_15S_MO.rnx"

lines = open(infile, "r").readlines()


def get_header(infile):
    lines = open(infile, "r").readlines()
    
    dict_infos = {}
    number_satellites = {}
    
    for line in lines:
        
        if "# OF SATELLITES" in line:
            break
        else:
                    
            info_obj = _remove_values(line[:60].split(" "))
            info_type = line[60:].title().replace(" ", "").replace("\n", "")
            dict_infos[info_type] = _remove_values(info_obj)

    return dict_infos
            
 

infos = get_header(infile)

infos

#%% 

def _split_number_of_obs(string:str) -> list:
    
    out = []
    for num in range(0, len(string), 6):
        elem = string[num: num + 6]
        try:
            convert = int(elem)
        except:
            convert = str(elem).strip()
            if convert == "":
                convert = np.nan
    
        out.append(str(convert))
        
    return out
    
def _fixed_format_of_obs(out):
    
    res = []
    
    for i in range(0, len(out), 2):
    
        list_sum = (out[i] + out[i + 1])
        
        if "S" in "".join(list_sum):
            res.append(out[i][:6])
            res.append(out[i + 1][:6])
        else:
            res.append(list_sum[:13])
        
    return res 


def _get_number_of_obs(infile):
    
    lines = open(infile, "r").read()
    
    num_start = lines.find("# OF SATELLITES")
    
    num_end = lines.find("INTERVAL")
    
    dat = lines[num_start: num_end].split('\n')[1:-1]
    
    out = []
    for item in range(len(dat)):
        element = dat[item][:60]
        sys_gnss = element.strip()[:1]
        
        if any(sys_gnss == j for j in ["R", "S", "G", "E"]): 
            
            out.append( _split_number_of_obs(element))
        else:
                   
            out.append(_split_number_of_obs(element)[1:])
            
    return _fixed_format_of_obs(out)


out = _get_number_of_obs(infile)

print(out)
#%%%

import datetime




def _get_interval_time(infile):
    
    lines = open(infile, "r").read()

    num_start = lines.find("INTERVAL")
    
    num_end = lines.find("END OF HEADER")
    
    dat = lines[num_start: num_end].split('\n')[1:-1]
    
    for j in range(2):
        elem = dat[j].split("   ")[:6]
        
        out = []
        for i in elem:
            new = str(int(float(i.strip())))
            if len(new) < 2:
                new = "0" + new
                
            out.append(new)
        
        print(datetime.datetime.strptime("".join(out), "%Y%m%d%H%M%S"))
    

