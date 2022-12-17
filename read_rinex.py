import pandas as pd
from datetime import datetime, timedelta
from gnss_utils import remove_values, get_interval, replace_values
import typing as T



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
        



class rinex(object):
    
    def __init__(self, infile):
        
        self.lines = open(infile, "r").readlines()

        self.attrs = header(infile).get()
        
   
    
    @property
    def _time_interval(self):

        first_obs = self.attrs['TimeOfFirstObs']
        interval = self.attrs["Interval"][0][:2]
        
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
    
    @staticmethod
    def _get_data_for_each_epoch(elem, prns, time):
        
        columns = []
        
        for j in range(len(elem)):
                
            elemlist = elem[j].lstrip().replace("\n", "")
            
            L1 = elemlist[0:13].strip()
            
            L1lli = elemlist[13:14].strip()
           
            C1 = elemlist[17:29].strip()
            
            L2 = elemlist[32:45].strip()
            
            L2lli = elemlist[45:46].strip()
            
            P2 = elemlist[47:61].strip()
            
            obs = replace_values([L1, L1lli, C1, L2, L2lli, P2])
            
            out = [time, prns[j]] + list(map(float, obs))
            
            #L1ssi = elemlist[14:15].strip()
            #L2ssi = elemlist[61:62].strip()
            #P2ssi = elemlist[62:63].strip()
            #C1ssi = elemlist[30:31].strip()
            columns.append(out)    
            
        return columns
    
    @property
    def _get_epochs(self):
        
        def _get_prns_rows(lines):
            
            epoch = []
            indexes = []
            
            for i in range(15, len(lines)):
                
                current = lines[i]
                            
                if any([i in current 
                        for i in ["G", "R", "E"]]):
                    epoch.append(current.strip())
                    indexes.append(i)
            return epoch, indexes
        
        epoch, indexes = _get_prns_rows(self.lines)
        
        epoch_fix = []
        indexes_fix = []
        
        for i in range(0, len(epoch) - 1, 2):
            
            res = (epoch[i] + epoch[i + 1]).split("  ")
            
            epoch_fix.append(res[-1][2:])
            indexes_fix.append(indexes[i])
        
        return self._split_prns(epoch_fix), indexes_fix
        
    @property
    def _get_rows_for_each_time(self):
            
        epoch, indexes = self._get_epochs
        times =  self._time_interval
        
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
                
            
            elem = self.lines[start: end]
            
            
            result.extend(self._get_data_for_each_epoch(elem, 
                                                   prns_list, 
                                                   time))
        return result
        
    def load(self):
        cols = ["time", "prn", "L1", "L1lli", "C1", 
                "L2", "L2lli", "P2"]
        result =  self._get_rows_for_each_time
        
        df = pd.DataFrame(result, columns = cols)
        
        df.index = df["time"]
        del df["time"]
        return df
    
    
infile = "database/rinex/2014/alar0011.14o"

lines = open(infile, "r").read()

dat = get_interval(lines, "END OF HEADER", None)


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

epoch, indexes = _get_prns_rows(dat)

def split_prns(item):
    
    return [item[num - 3: num] for num in 
            range(3, len(item[2:]) + 3, 3)]

prns_infos = []
datetime_infos = []

for i in range(0, len(epoch) - 1, 2):
    

    res = (epoch[i] + epoch[i + 1]).split("  ")
    
    prns_infos.append(split_prns(res[-1][4:].strip()))
    datetime_infos.append(res[:-1])

prns_infos.append(epoch[-1])
datetime_infos.append(epoch[-1])

epoch = len(prns_infos)

#satellites = int(epoch[:2])

#item = epoch[2:]


print(epoch)

    
    
    
    
    
    
    
    
    
    
    