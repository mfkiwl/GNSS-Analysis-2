import pandas as pd
from datetime import datetime
from gnss_utils import remove_values, get_interval, sep_elements
import typing as T

import numpy as np


remove_in_rinex2 = ["Type", "#", 
                    'Pgm',
                    'RunBy',
                    'TypesOfObserv', 
                    'Rec#', 
                    'WavelengthFactL1',
                    'Antenna:DeltaH',
                    'E',
                    'N',
                    '2',
                    "Vers", 
                    'Observer']

remove_in_rinex3 = ['GlonassSlot', 
                    'Pgm',
                    'Date',
                    '#',
                    'Sys', 
                    'Antenna:DeltaH', 
                    'E',
                    'N',
                    'Comment',
                    'Vers',
                    'Ant#',
                    'Observer', 
                    'Rec#', 
                    'Prn', 
                    'RunBy', 
                    'Type']  

class header(object):
    
    """Get header from Rinex 2 and 3"""
    
    def __init__(self, infile: T.TextIO):
        
        
        self.lines = open(infile, "r").read()
    
    @staticmethod
    def remove_keys(dat: dict):

        if dat['RinexVersion'][0] == "2":
            remove_list = remove_in_rinex2 
        else:
            remove_list = remove_in_rinex3 

        for key in remove_list:
            del dat[key]
            
        return dat
    
    @staticmethod
    def sep_key_by_string(dat: dict, 
                          string: str = "/"):
        dict_out = {}
        for key in dat.keys():
            
            if string in key:
                for nkey, value in zip(key.split(string), 
                                       dat[key]):
                    dict_out[nkey] = value  
                    
            else:
                dict_out[key] = dat[key]
                
        return dict_out

    def get(self, arg = None):
        
        dat = get_interval(self.lines, 
                           start = "", 
                           end = "END OF HEADER", 
                           snum = 0)
        out_dict = {}
        
        for line in dat:
            info_obj = remove_values(line[:60].split("   "))
           
            info_type = line[60:].title().replace(" ", "").replace("\n", "")
            
            out_dict[info_type] = remove_values(info_obj)
            
        result = self.remove_keys(self.sep_key_by_string(out_dict))
        
        if arg is None:
            return result
        else:
            return result[arg] 
            


def split_prns(item):
    
    return [item[num - 3: num] for num in 
            range(3, len(item[2:]) + 3, 3)]

def get_prns_rows(dat):
    
    """
    Get rows which have prns and datetime information
    """
    
    epoch = []
    indexes = []
    datetime_infos = []
    

    for i in range(len(dat) - 1):
        
        first = dat[i]
        second = dat[i + 1]
        
        if (any([i in first for i in ["G", "R", "E"]]) and 
            (any([i in second for i in ["G", "R", "E"]]))):
            
            current = (first + second.strip()).split("  ")
            epoch.append(split_prns(current[-1][4:].strip()))
            datetime_infos.append(" ".join(current[:-1]).strip())
            indexes.append(i + 2)
            
    return epoch, indexes, datetime_infos




    
def sep_elements2(elem, length = 16):
    out = []
    for num in range(0, 63, length):
        item = elem[num: num + length].strip()
        if item == "":
            out.append(np.nan)
        else:
            out.append(item)
    return out




def get_parameters(item):
    
    """
    Separe string into observables values, 
    lost lock indicators (lli) and
    strength signal indicators (ssi) 
    """
    

    obs_vals = []
    ssi_vals = []
    lli_vals = []
    
    for i in range(len(item)):
        
        if item[i] != item[i]:
            obs_vals.append(np.nan)
            ssi_vals.append(np.nan)
            lli_vals.append(np.nan)
        else:
            obs = item[i][:-2]
            ssi = item[i][-1:].strip()
            lli = item[i][-2:-1].strip()
            
            if lli == "": lli = np.nan
            if ssi == "": ssi = np.nan
            
            obs_vals.append(float(obs))
            ssi_vals.append(float(ssi))
            lli_vals.append(float(lli))
        
    return lli_vals, ssi_vals, obs_vals


def get_epochs(element: list, 
               prns: list, 
               time: str):
    res = []
    for i in range(len(element)):
        join = [time.strip(), prns[i]]
        join.extend(sep_elements2(element[i]))
        res.append(join)
    
    return res

def get_datetime(time):
    t = time.split(" ")
    return datetime(int("20" +  t[0]), 
                   int(t[1]), 
                   int(t[2]), 
                   int(t[3]), 
                   int(t[4]), 
                   int(float(t[5])))


    
        
    #return pd.DataFrame(res)



class rinex:
    
    def __init__(self, infile):
        
        lines = open(infile, "r").read()
    
        dat = get_interval(lines, "END OF HEADER", None)
        
        epoch, indexes, datetime_infos = get_prns_rows(dat)

        self.res_lli = []
        self.res_ssi = []
        self.res_vals = []
        for num in range(len(indexes) - 1):
            
            id1 = indexes[num]
            id2 = indexes[num + 1] - 2
            
            item = dat[id1: id2]
            
            time = datetime_infos[num]
            
            prns = epoch[num]
            
           
            for i in range(len(item)):
                
                lli, ssi, vals = get_parameters(sep_elements2(item[i]))
                
                self.res_vals.append([get_datetime(time), prns[i]] + vals)
                self.res_lli.append([get_datetime(time), prns[i]] + lli)
                self.res_ssi.append([get_datetime(time), prns[i]] + ssi)
        
        last = dat[indexes[-1]:]
        for i in range(len(item)):
            lli, ssi, vals = get_parameters(sep_elements2(last[i]))
           
            self.res_vals.append([get_datetime(datetime_infos[-1]), 
                             prns[-1]] + vals)
            self.res_lli.append([get_datetime(datetime_infos[-1]), 
                            prns[-1]] + lli)
            self.res_ssi.append([get_datetime(datetime_infos[-1]), 
                            prns[-1]] + ssi)
    @property
    def lli(self):
        columns = ["time", "prn", "L1lli", "", "L2lli", ""]
        df = pd.DataFrame(self.res_lli, columns = columns)
        df.index = df.time
        del df["time"], df[""]
        for col in ["L1lli", "L2lli"]:
            df.replace({col: {np.nan: 0}}, inplace = True)
        return df 
    
    @property
    def ssi(self):
        columns = ["time", "prn", "L1ssi", "C1ssi", "L2ssi", "P2ssi"]
        df =  pd.DataFrame(self.res_ssi, columns = columns)
        df.index = df.time
        del df["time"]
        return df
    
    @property
    def obs(self):
        columns = ["time", "prn", "L1", "C1", "L2", "P2"]
        df = pd.DataFrame(self.res_vals, columns = columns)
        df.index = df.time
        del df["time"]
        df = df.dropna(subset = columns[2:])
        return df


def main():
    infile = "database/rinex/2014/alar0011.14o"
    
    
    df = rinex(infile).lli

    
    #df1 = df.loc[df["prn"] == "R04", "P2"]
    print(df)
    
main()


