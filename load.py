# -*- coding: utf-8 -*-
"""
Created on Tue Aug  9 10:24:16 2022

@author: Luiz
"""

import georinex as gr
import pandas as pd
import numpy as np
import datetime

def load_receiver(receiver_path, prn = None):

    obs = gr.load(receiver_path, 
                  useindicators = True)

    if prn == None:
        df = obs.to_dataframe()

    else:
        df = obs.sel(sv = prn).to_dataframe()

    try:
        df = df.drop(columns = ["P1", "P2ssi", "P1ssi",
                                "C1ssi", "L1ssi", "L2ssi"])

    except:
        df = df.drop(columns = ["P2ssi", "C1ssi",
                                "L1ssi", "L2ssi"])

    df = df.dropna(subset = ["L1", "L2", "C1", "P2"])

    for col in ["L1lli", "L2lli"]:
        df.replace({col: {np.nan: 0}}, inplace = True)

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
            
            self.pos = self.pos.reindex(pd.date_range(start = start, end = end, freq = interpol))

            self.pos = self.pos.interpolate(method='spline', order = 5)
            
            self.pos.columns.names = [self.prn]
        
        return self.pos
    
    
    
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
        


def main():
    receiver_path = "Database/alar0011/alar0011.14o"
    orbital_path = "Database/jpl17733.sp3/igr17733.sp3"
