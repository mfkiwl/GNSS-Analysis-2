# -*- coding: utf-8 -*-
"""
Created on Tue Aug  9 10:24:16 2022

@author: Luiz
"""

import georinex as gr
import pandas as pd
import numpy as np
import datetime
import os
from utils import doy_str_format, create_directory
import json 
import ast
from build import build_paths

def get_infos_from_rinex(ds):
    
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


def load_receiver(receiver_path: str,
                  observables: list = ["L1", "L2", "C1", "P2"],
                  lock_indicators: list = ["L1lli", "L2lli"],
                  attrs: bool = True):
    
    """Load RINEX file (receiver measurements)"""

    
    obs = gr.load(receiver_path, 
              useindicators = True, 
                  fast = False)
    
    df = obs.to_dataframe()
        
        
    df = df.loc[:, observables + lock_indicators]
    
    df = df.dropna(subset = observables)

    for col in lock_indicators:
        df.replace({col: {np.nan: 0}}, inplace = True)
        
    if attrs:
        return df, get_infos_from_rinex(obs)
    else:
        return df

class load_orbits(object):
    
    """Read orbit data (CDDIS Nasa) with interpolation method"""

    def __init__(self, orbital_path, prn = "G01"):
        
        self.orbital_path = orbital_path
        self.prn = prn

        self.ob = gr.load(self.orbital_path).sel(sv =  self.prn).to_dataframe()
        
        self.time = pd.to_datetime(np.unique(self.ob.index.get_level_values('time')))


    def position(self, interpol:str = "30s"):
    
        pos_values = {}
        
        for coord in ["x", "y", "z"]:
            
            pos_values[coord] = self.ob.loc[self.ob.index.get_level_values("ECEF") == coord, 
                               ["position"]].values.ravel()

        self.pos = pd.DataFrame(pos_values, index = self.time)
        
        if interpol:
            end = self.pos.index[0] + datetime.timedelta(hours = 23, 
                                                         minutes = 59, 
                                                         seconds = 30)
            start = self.pos.index[0]
            
            self.pos = self.pos.reindex(pd.date_range(start = start, 
                                                      end = end, 
                                                      freq = interpol))

            self.pos = self.pos.interpolate(method = 'spline', order = 5)
            
            self.pos.columns.names = [self.prn]
        
        return self.pos
    
def run_for_all_files(year: int, 
                      doy: int, 
                      extension: str = ".22o"):
    
    """Processing all data for one single day"""
    
    path = build_paths(year, doy)
    rinex_path = path.rinex
    
    _, _, files = next(os.walk(rinex_path))

    out_dict = {}
    
    path_process = create_directory(path.process)

    for filename in files:
        
        
        if filename.endswith(extension):

            name_to_save = filename[:4]
            
            try:
                df, attrs = load_receiver(os.path.join(rinex_path, filename))
                
    
                df.to_csv(os.path.join(path_process, name_to_save + ".txt"), 
                              sep = " ", index = True)
                
                out_dict.update(attrs)
                print(f"{name_to_save} got it!")
            except:
                print(f"{name_to_save} doesn't work!")
                continue
    return out_dict


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
        

def read_all_processed(year: int, 
                       doy: int, 
                       station: str) -> pd.DataFrame:
    
    """Read all processed data (only for my local repository)"""

    filename  = f"{station}.txt"

    infile = build_paths(year, doy).all_process

    df = pd.read_csv(infile + filename, 
                     delim_whitespace = True, 
                     index_col = "time")

    df.index = pd.to_datetime(df.index)

    return df


def main():
    
    year = 2022
    for doy in range(2, 5): 
        path = build_paths(year, doy)
        path_json = path.fn_json

        out_dict = run_for_all_files(year, doy, extension = ".22o")
        save_attrs(path_json, out_dict)
    
