from gnss_utils import remove_values, replace_values, find, sep_elements, get_interval
import numpy as np
import datetime
import pandas as pd
from read_rinex import header


infile = "database/rinex/ALMA00BRA_R_20182440000_01D_15S_MO.rnx"


class rinex3(object):
    
    def __init__(self, infile):
        
        self.lines = open(infile, "r").read()
        self.indexes = find(self.lines, ">")
        self.attrs = header(infile).get()
        
    @property    
    def _get_glonass_slot(self):

        dat =  get_interval(self.lines, 
                            "OBSERVER / AGENCY", 
                            "GLONASS COD/PHS/BIS")
        out = {}
        for j in range(len(dat)):
            elem = remove_values(dat[j][:60].split(" "))
            
            if elem[0] == "24":
                elem = elem[1:]
            
            for i in range(0, len(elem) - 1, 2):
                
                out[elem[i]] = elem[i + 1]
            
        return out
    
    @property
    def interval_time(self):
         
        dat = get_interval(self.lines, 
                           "INTERVAL", 
                           "END OF HEADER")
        res = []
        
        for j in range(2):
            elem = dat[j].split("   ")[:6]
            
            year = int(elem[0].strip())
            month = int(elem[1].strip())
            day = int(elem[2].strip())
            
            hour = int(elem[3].strip())
            minute= int(elem[4].strip())
            sec = int(float(elem[5].strip()))
            
            res.append(datetime.datetime(year, month, day,
                                         hour, minute, sec))
            
        return pd.date_range(res[0], res[1], freq = "15s")
    
    
    def _get_columns(self, string_column, time):
        
        def _get_rows(string_row, time):    
            
            res = [time, string_row[:5].strip()]

            sections = [string_row[5:67], 
                        string_row[67:131], 
                        string_row[131:]]
            
            for item in sections:
            
                res.extend(replace_values(sep_elements(item, 
                                                        length = 16)))
            if len(res) != 13:
                res.extend([np.nan] * (13 - len(res)))
                       
            return res
        
        result = []
        for item in range(len(string_column)):
        
            if  string_column[item][:1] == "S": # Fix for this constellation
                continue
            else:
                result.append(_get_rows(string_column[item],
                                        time))
        return result
    
    def _get_row_data(self):
        result = []
        times = self.interval_time

        for num in range(0, len(self.indexes) - 1):
            
            elem = self.lines[self.indexes[num]: 
                      self.indexes[num + 1]].split("\n")[1:-1]
            
            result.extend(self._get_columns(elem, times[num]))
        
        elem = self.lines[self.indexes[-1]:].split("\n")[1:-1]
        result.extend(self._get_columns(elem, times[-1]))
            
        return result
    
    @property
    def number_of_obs(self):
        
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
        
        
    
        dat =  get_interval(self.lines, 
                             "# OF SATELLITES", 
                                  "INTERVAL")
        
        out = []
        for item in range(len(dat)):
            element = dat[item][:60]
            sys_gnss = element.strip()[:1]
            
            if any(sys_gnss == j for j in ["R", "S", "G", "E"]): 
                
                out.append( _split_number_of_obs(element))
            else:
                       
                out.append(_split_number_of_obs(element)[1:])
                
        return _fixed_format_of_obs(out)
    
    def get_prn_count(self, prn = "E08"):
        """Get observables total count for an prn (input)"""
        
        dat = self.number_of_obs
        for i in dat:
            
            if prn == i[0]:
                return i
            else:
                raise TypeError(f"The {prn} doesnt exist in this file")
                
                
    @property
    def _get_obs_types(self):
           
        dat =  get_interval(self.lines, "ANT # / TYPE",  
                            "# OF SATELLITES")
        
        sys_obstype = {}
        for i in range(len(dat)):
            elem = remove_values(dat[i][:60].split(" "))
            sys_obstype[elem[0]] = elem[2:]
        
        return sys_obstype
    
    def _get_gnss_types(self, gnss = "E"):
        
        """Check the first element in string 
        for to separe the observables"""
        
        dat = self._get_obs_types
        pseudos = []
        carries = []
        signals = []
        
        for obs in dat[gnss]:
            
            if obs[:1] == "C":
                pseudos.append(obs)
            elif obs[:1] == "L":
                carries.append(obs)    
            else:
                signals.append(obs)
            
        return pseudos, carries, signals
    
    @staticmethod
    def _get_signal(row):
        return row[:2] + list(map(float, row[10:]))
    
    @staticmethod
    def _get_pseudoranges(row):
        tp = row[:2]
        items = row[2:6]
        P = []
        ssi = []
        for obs in items:
            
            if obs != obs:
                P.append(obs)
                ssi.append(obs)
            else:
                value = float(obs[:-2])
                ssi_ = int(obs[-2:].strip())
                
                P.append(value)
                ssi.append(ssi_)
        return tp + P, tp + ssi


    @staticmethod
    def _get_carrierphases(row):
        items = row[6:10]
        tp = row[:2]
        Ls = []
        llis = []
        ssis = []
        for obs in items:
            if obs!= obs:
                Ls.append(obs)
                llis.append(obs)
                ssis.append(obs)
                
            else:
                value = float(obs[:-2])
                lli = obs[-2:-1].strip()
                ssi = int(obs[-1].strip())
                
                if lli == "":
                    lli = np.nan
                else:
                    lli = int(lli)
                    
                Ls.append(value)
                llis.append(lli)
                ssis.append(ssi)
        return tp + Ls, tp + llis, tp + ssis
    
    def _get_all_data(self, 
             mode = "pseudorange", 
             lli = False, 
             gnss = "E"):
        
        out = self._get_row_data()
        res = []
        for num in range(len(out)):
            if out[num][1][:1] == gnss:
                if mode == "pseudorange":
                    P, ssi = self._get_pseudoranges(out[num])
                    res.append(P)
                elif mode == "carrierphase":
                    Ls, llis, ssis = self._get_carrierphases(out[num])
                    res.append(Ls)
                elif mode == "signal":      
                    res.append(self._get_signal(out[num]))
            
        return res
    
    
    def load(self, 
             mode = "pseudorange", 
             lli = False, 
             gnss = "E"):
        
        dat = self._get_all_data(mode = mode, 
                 lli = False, gnss = gnss)
        
        p, c, s = self._get_gnss_types(
                                       gnss = gnss)
        
        if mode == "pseudorange":
            columns = ["time", "prn"] + p
        elif mode == "carrierphase":
            columns = ["time", "prn"] + c
        else:
            columns = ["time", "prn"] + s
        
        return pd.DataFrame(dat, columns = columns)
    
  


def main():
    
    ge = rinex3(infile)

    df = ge.load(mode = "pseudorange", gnss = "G")
    
    #df["time"] = pd.to_datetime(df["time"])
    print(df)
    #print(ge._get_gnss_types(gnss = "G"))
    
    #plt.plot(df1["time"], df1["L8X"])        


#main()