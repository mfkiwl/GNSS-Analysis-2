# -*- coding: utf-8 -*-
"""
Created on Tue Aug  9 10:24:16 2022

@author: Luiz
"""

import georinex as gr
import pandas as pd


class load_orbits(object):
    
    def __init__(self, infile, filename, prn = "G05"):
        
        
        ob = gr.load(infile + filename).to_dataframe()
        
        self.ob = ob.loc[ob.index.get_level_values("sv") == prn, :]
    
    
    def position(self, pos = "x"):
        position = self.ob.loc[self.ob.index.get_level_values("ECEF") == pos, 
                               ["position"]]
        position.index = pd.to_datetime(position.index.get_level_values(0))
        return position
    

class load_receiver(object):
    
    def __init__(self, infile, filename, prn = "G05"):
        
        self.obs = gr.load(infile + filename)
        rx = self.obs.to_dataframe()
    
    @property
    def position(self):
        return self.obs.position
    
        #rx = rx.dropna()
    
        #rx = rx.loc[rx.index.get_level_values("sv") == prn, :]
    
        #rx.index = pd.to_datetime(rx.index.get_level_values("time"))