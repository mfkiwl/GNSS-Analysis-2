import pandas as pd
from datetime import datetime
from gnss_utils import remove_values, get_interval
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
    def remove_keys(dat: dict) -> dict:

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
            

def floatornan(x):
    if x == '' or x[-1] == ' ':
        return np.nan
    else:
        return float(x)

def digitorzero(x):
    if x == ' ' or x == '':
        return 0
    else:
        return int(x)

def split_prns(item: str) -> list:
    """Split PRNs string sequence into list"""
    return [item[num - 3: num] for num in 
            range(3, len(item[2:]) + 3, 3)]

        
def get_datetime(string_time: str) -> datetime:
    """Convert datetime location into datetime"""
    t = remove_values(string_time.split(" "))
    return datetime(int("20" +  t[0]), 
                   int(t[1]), 
                   int(t[2]), 
                   int(t[3]), 
                   int(t[4]), 
                   int(float(t[5])), 
                   int(t[6]))
 
def chunk_epochs(sats):  
    
    prns_list = []
    count_prn = []
    time_list = []  
    
    for i in range(len(sats) - 1):
        first = sats[i]
        secon = sats[i + 1]
        
        if len(first) > 62:
            epoch = "".join([first, secon])
            num_sats = int(epoch[29:][:2].strip())
            
            _prns = split_prns(epoch[29:][2:])
            
            if len(_prns) != num_sats:
                raise "Something it wrong with the prns"
            else:
                prns_list.extend(_prns)
                count_prn.append(num_sats)
            time_list.extend([get_datetime(epoch[:29])] 
                             * num_sats)
            
    time_list = np.array(time_list, 
                          dtype = 'datetime64[us]')
    
    
    return prns_list, time_list, count_prn


def get_obs(prns_list, obs_epoch):
    
     
    """
    Separe string into observables values, 
    lost lock indicators (lli) and
    strength signal indicators (ssi) 
    """
    
    total_sats = len(prns_list)
    obs_types = 4
    
    obs = np.empty((total_sats, obs_types), 
                   dtype = np.float64) * np.NaN
    
    lli = np.zeros((total_sats, obs_types), 
                   dtype = np.uint8)
    
    ssi = np.zeros((total_sats, obs_types), 
                               dtype = np.uint8)
    
    for i in range(total_sats):
        
        obs_line = obs_epoch[i]
    
        for j in range(obs_types):
            obs_record = obs_line[16 * j: 16*(j + 1)]  
                
            obs[i, j] = floatornan(obs_record[0:14])
            lli[i, j] = digitorzero(obs_record[14:15])
            ssi[i, j] = digitorzero(obs_record[15:16])
            
    return obs, lli, ssi


def get_epochs(dataSection):
       
    obs_epoch = []
    sat_epoch = []
    
    for elem in dataSection:
                
        if any([i in elem.strip() 
                for i in ["G", "R", "E"]]):
            sat_epoch.append(elem.strip())
        else:
            obs_epoch.append(elem)
            
    return obs_epoch, sat_epoch


class RINEX2:
    
    def __init__(self, infile: T.TextIO):
        
        stringText = open(infile, "r").read()

        start = stringText.find("END OF HEADER")
        
        dataSection = stringText[start: None].split("\n")[1:-1]
        
        obs_epoch, sat_epoch = get_epochs(dataSection)
        
        self.prns_list, self.time_list, count_prn = chunk_epochs(sat_epoch)
            
        self._obs, _lli, self._ssi = get_obs(self.prns_list, obs_epoch)
        
        # Remove "loss lock indicator" for C1 and P2 
        self._lli = np.delete(_lli, slice(1, 3), axis = 1)
        
        self.dat = np.concatenate([self._obs, 
                                   self._lli], axis = 1)
        
        
    def data(self, data, columns):
        
        arrays = [self.time_list, self.prns_list]

        tuples = list(zip(*arrays))

        index = pd.MultiIndex.from_tuples(tuples, 
                                          names = ["time", "prn"]) 
        
        df = pd.DataFrame(data, 
                          columns = columns, 
                          index = index)
        df = df.dropna(subset = ["L1", "C1", "L2", "P2"])
        return df
    
    @property
    def obs(self):
        columns  = ["L1", "C1", "L2", "P2"]
        return self.data(self._obs, columns)
    
    @property
    def lli(self):
        columns  = ["L1", "L2"]
        return self.data(self._lli, columns)
    
    @property
    def ssi(self):
        columns  = ["L1", "C1", "L2", "P2"]
        return self.data(self._ssi, columns)
    
         
    def sel(self, prn):
        """Select obsevables and lli for phases"""
        columns  = ["L1", "C1", "L2", 
                    "P2", "L1lli", "L2lli"]
        df = self.data(self.dat, columns)
        df = df.loc[df.index.get_level_values("prn") == prn]
        
        df.index = pd.to_datetime(df.index.get_level_values("time"))
        
        df.columns.name = prn
        return df


def main():
    infile = "database/rinex/2014/alar0011.14o"
    
    prn = "G01"
    df = RINEX2(infile).sel(prn)
    
    print(df)
    
