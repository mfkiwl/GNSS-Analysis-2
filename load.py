import georinex as gr
import pandas as pd
import numpy as np
import datetime
import json 
import ast



def get_infos_from_rinex(ds) -> dict:
    
    """Getting attributes from dataset (netcdf file) into dictonary"""
    
    position  = ds.attrs["position"]
    station = ds.attrs["filename"][:4]
    rxmodel = ds.attrs["rxmodel"]
    time_system = ds.attrs["time_system"]
    version = ds.attrs["version"]


    y = {}
    x =  {"position": position, 
          "rxmodel": rxmodel, 
          "time_system": time_system, 
          "version": version}

    y[station] = x
            
    return y

class load_receiver(object):

    """Load RINEX file (receiver measurements)"""

    def __init__(self, receiver_path: str,
                  observables: list = ["L1", "L2", "C1", "P2"],
                  lock_indicators: list = ["L1lli", "L2lli"],
                  attrs: bool = True, 
                  fast: bool = False):
        
        self.receiver_path = receiver_path
        self.obs = gr.load(self.receiver_path, 
                      useindicators = True, 
                      fast = fast)

        self.df = self.obs.to_dataframe()

        self.df = self.df.loc[:, observables + lock_indicators]

        self.df = self.df.dropna(subset = observables)

        for col in lock_indicators:
            self.df.replace({col: {np.nan: 0}}, inplace = True)
        
     
    @property
    def attrs(self):
        """Files attributes (dictionary like)"""
        return get_infos_from_rinex(self.obs)
    @property
    def prns(self):
        """PRNs list (numpy array like)"""
        return self.obs.sv.values


def interpolate_orbits(infile: str, 
                       prn: str, 
                       parameter: str = "position") -> pd.DataFram:
    
    obs = gr.load(infile)
    
    df = obs.sel(sv = prn).to_dataframe()
    
    time = pd.to_datetime(np.unique(df.index.get_level_values('time')))
    
    coord_values = {}

    for coord in ["x", "y", "z"]:

        coord_values[coord] = df.loc[df.index.get_level_values("ECEF") == coord, 
                                   [parameter]].values.ravel()

    res = pd.DataFrame(coord_values, index = time)

    start = res.index[0]

    end = start + datetime.timedelta(hours = 23, minutes = 59, seconds = 30)

    res = res.reindex(pd.date_range(start = start, end = end, freq = "30s"))
    
    res.columns.names = [prn]
    
    return res.interpolate(method = 'spline', order = 5)


def save_attrs(path: str, out_dict: dict):
    """Save attributes in json file"""
    json_data = ast.literal_eval(json.dumps(out_dict))
    
    with open(path, 'w') as f:
        json.dump(json_data, f)
        

    
class observables(object):
    
    """Load observables from dataframe already processed"""
    
    def __init__(self, df: pd.DataFrame, prn = None):
        
        self.df = df 
        self.prns = np.unique(self.df.index.get_level_values('sv').values)
        
        if prn is not None:
            obs = self.df.loc[self.df.index.get_level_values('sv') == prn, :]
        else:
            obs = self.df
    
        self.l1 = obs.L1.values
        self.l2 = obs.L2.values
        self.c1 = obs.C1.values
        self.p2 = obs.P2.values
        
        self.l1lli = obs.L1lli.values.astype(int)
        self.l2lli = obs.L2lli.values.astype(int)
        
        self.time = pd.to_datetime(obs.index.get_level_values('time'))
        


