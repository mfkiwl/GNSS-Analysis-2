from read_rinex import _remove_values, _replace_values
import numpy as np
import datetime

infile = "database/rinex/ALMA00BRA_R_20182440000_01D_15S_MO.rnx"

lines = open(infile, "r").read()

def find(s, ch):
    return [i for i, ltr in enumerate(s) if ltr == ch]
indexes = find(lines, ">")


#%%

def sep_elements(list_to_sep, length = 16):
    
    return [list_to_sep[num: num + length].strip() for num in 
            range(0, len(list_to_sep), length)]


def get_rows(a):    
    res = [a[:5].strip()]
    
   
    sections = [a[5:67], a[66:130], a[130:]]
    
    for item in sections:
    
        res.extend(_replace_values(sep_elements(item, 
                                                length = 16)))
    if len(res) != 13:
        res.extend([np.nan] * (13 - len(res)))
        
    
    return res


def get_columns(a):
    
    out = []
    for i in range(len(a)):
    
        b = a[i]
        
        if b[:1] == "S":
            continue
        else:
            out.append(get_rows(b))
    return out


out = []

#for num in range(0, len(indexes), 2):
    
    
   # out.append(get_columns(a))
    
a = lines[indexes[-3]:indexes[-2]].split("\n")#[1:-1]
print(a)

#%%%

def _get_obs_types(infile):
    
    lines = open(infile, "r").read()
    
    num_start = lines.find("ANT # / TYPE")
    
    num_end = lines.find("# OF SATELLITES")
    
    dat = lines[num_start: num_end].split('\n')[1:-1]
    
    sys_obstype = {}
    for i in range(len(dat)):
        elem = _remove_values(dat[i][:60].split(" "))
        sys_obstype[elem[0]] = elem[2:]
    
    return sys_obstype


def _get_glonass_slot(infile):

    lines = open(infile, "r").read()
    
    num_start = lines.find("OBSERVER / AGENCY")
    
    num_end = lines.find("GLONASS COD/PHS/BIS")
    
    dat = lines[num_start: num_end].split('\n')[1:-1]
    
    out = {}
    for j in range(len(dat)):
        elem = _remove_values(dat[j][:60].split(" "))
        
        if elem[0] == "24":
            elem = elem[1:]
        
        for i in range(0, len(elem) - 1, 2):
            
            out[elem[i]] = elem[i + 1]
        
    return out

def _get_header(infile):
    lines = open(infile, "r").read()
    
    num_start = 0# lines.find("")
    
    num_end = lines.find("OBSERVER / AGENCY")
    
    dat = lines[num_start: num_end].split('\n')[:-1]
    
    out = {}
    for line in dat:
        info_obj = _remove_values(line[:60].split("   "))
       
        info_type = line[60:].title().replace(" ", "").replace("\n", "")
        
        out[info_type] = _remove_values(info_obj)
    
    return out
#%% 

def _split_number_of_obs(string: str) -> list:
    
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



#%%%





def _get_interval_time(infile):
    
    lines = open(infile, "r").read()

    num_start = lines.find("INTERVAL")
    
    num_end = lines.find("END OF HEADER")
    
    dat = lines[num_start: num_end].split('\n')[1:-1]
    
    res = []
    
    for j in range(2):
        elem = dat[j].split("   ")[:6]
        
        year = int(elem[0].strip())
        month = int(elem[1].strip())
        day = int(elem[2].strip())
        
        hour = int(elem[3].strip())
        minute= int(elem[4].strip())
        sec = int(float(elem[5].strip()))
        
        res.append(datetime.datetime(year, month, day, hour, minute, sec))
        
    return tuple(res)
    
print(_get_interval_time(infile))
