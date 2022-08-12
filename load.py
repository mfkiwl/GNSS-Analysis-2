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


def find_header(infile:str, 
                filename: str, 
                header: str = 'yyyy.MM.dd') -> tuple:

    """Function for find the header and the data body"""

    with open(infile + filename) as f:
        data = [line.strip() for line in f.readlines()]

    count = 0
    for num in range(len(data)):
        if (header) in data[num]:
            break
        else:
            count += 1


    data_ = data[count + 2: - 3]


    header_ = data[count + 1].split(" ")

    return (header_, data_)

    
    
infile = "Database/CAS0MGXRAP_20140010000_01D_01D_DCB.BSX/"
filename = "CAS0MGXRAP_20140010000_01D_01D_DCB.BSX"

def read_dcb(infile, filename):

    header, data = find_header(infile,
                filename, 
                header = '+BIAS/SOLUTION')



    def _extract_elements(dat):
        BIAS = dat[:5].strip()
        version = dat[5:9].strip()
        file_agency = dat[9:13].strip()
        creation_time = dat[13:18].strip()
        code = dat[18: 28].strip()

        return [BIAS, version, file_agency, creation_time, code] + dat[28:].split()


    str_data =  [_extract_elements(num) for num in data]

    names = ["bias", "svn", "prn", "site", 
            "domes", "obs1", "obs2", "b_start", 
            "b_end", "unit", "value", "std"]


    df = pd.DataFrame(str_data, columns = names)

    df[["value", "std"]] = df[["value", "std"]].apply(pd.to_numeric, 
                                                      errors='coerce')

    return df




def main():
    receiver_path = "Database/alar0011/alar0011.14o"
    orbital_path = "Database/jpl17733.sp3/igr17733.sp3"
    
    df = join_orbits_with_receiver(receiver_path, 
                                  orbital_path, save = True)
    
    df
    
