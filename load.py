# -*- coding: utf-8 -*-
"""
Created on Tue Aug  9 10:24:16 2022

@author: Luiz
"""

import georinex as gr
import pandas as pd
import numpy as np

def join_orbits_with_receiver(receiver_path: str, 
                              orbital_path: str, 
                              save: bool = False, 
                              useindicators: bool = True) -> pd.DataFrame:
    
    y = gr.load(receiver_path, useindicators = useindicators).to_dataframe()
   

    x = gr.load(orbital_path).to_dataframe()
        
    df = x.join(y.reindex(y.index, level = 0))
    
    if useindicators:
        slip_cols = [elem for elem in list(df.columns)
                     if ("ssi" in elem) or ("lli" in elem)]


    for col in slip_cols:
        df.replace({col: {np.nan: 0}}, inplace = True)

    df = df.dropna()
    
    if save:
        df.to_csv("Database/process.txt", sep = " ", index = True)
    
    return df


receiver_path = "Database/alar0011/alar0011.14o"
orbital_path = "Database/jpl17733.sp3/igr17733.sp3"

df = join_orbits_with_receiver(receiver_path, 
                              orbital_path, save = True)

df
    
