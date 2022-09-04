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

def get_infos_from_rinex(ds):
    """Getting attributes from dataset"""
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


def load_receiver(receiver_path, attrs = True):
    
    """Load RINEX file (receiver measurements)"""

    obs = gr.load(receiver_path, 
                  useindicators = True)
    
    df = obs.to_dataframe()
    
    try:
        df = df.drop(columns = ["P1", "P2ssi", "P1ssi",
                                "C1ssi", "L1ssi", "L2ssi"])

    except:
        df = df.drop(columns = ["P2ssi", "C1ssi",
                                "L1ssi", "L2ssi"])

    df = df.dropna(subset = ["L1", "L2", "C1", "P2"])

    for col in ["L1lli", "L2lli"]:
        df.replace({col: {np.nan: 0}}, inplace = True)
    if attrs:
        return df, get_infos_from_rinex(obs)
    else:
        return df

class load_orbits(object):
    
    """Read orbit data (CDDIS Nasa)"""

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
    
def run_for_all_files(year, doy):
    
    """Processing all data for one single day"""
    
    infile = f"Database/rinex/{year}/{doy_str_format(doy)}/"

    _, _, files = next(os.walk(infile))

    out_dict = {}
    
    path_out = create_directory("G://My Drive//Python//data-analysis//GNSS//Database//process//", year, doy)

    for filename in files:

        rinex_path = os.path.join(infile, filename)
        pfilename = filename.replace(".14o", "")[:-1]    
        
        try:

            df, attrs = load_receiver(rinex_path)

            df.to_csv(os.path.join(path_out, pfilename + ".txt"), 
                          sep = " ", index = True)
            out_dict.update(attrs)

        except:
            print(f"{filename} doesn't work")
            continue
    return out_dict


def save_attrs(path, out_dict):
    """Save attributes with json"""
    json_data = ast.literal_eval(json.dumps(out_dict))
    
    with open(path, 'w') as f:
        json.dump(json_data, f)

    
class observables(object):
    
    """Load observables from dataframe already processed"""
    
    def __init__(self, df, prn = None):
        
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
        

def read_all_processed(year, doy, station):
    
    """Read all processed data (only for my local repository)"""

    filename  = f"{station}{doy_str_format(doy)}"

    infile = f"Database/all_process/{year}/{station}/{filename}.txt"

    df = pd.read_csv(infile, delim_whitespace = True)

    df.index = pd.to_datetime(df.time)

    return df


def main():
    
    year = 2014
    doy = 1
    path_json = 'Database/json/stations.json'
    out_dict = run_for_all_files(year, doy)
    save_attrs(path_json, out_dict)

#main()