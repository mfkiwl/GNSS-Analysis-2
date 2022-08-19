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
    
    


    obs = gr.load(receiver_path, useindicators = True)
    
    rinex = obs.to_dataframe()

    for col in ["P2ssi", "P1ssi", "C1ssi", "L1ssi", "L2ssi"]:
        try: 
            rinex.drop(columns = col, inplace = True)

        except:
            continue

    rinex = rinex.dropna(subset = ["L1", "L2", "C1", "P2"])

    for col in ["L1lli", "L2lli"]:
        rinex.replace({col: {np.nan: 0}}, inplace = True)

    

    orbits = gr.load(orbital_path).to_dataframe()


    orbits.drop(columns = ["clock", "dclock"], inplace = True)

    df = orbits.join(rinex.reindex(rinex.index, level = 1))

    df = df.dropna()


    if save:
        
        
        time_system = obs.attrs["time_system"]
        station = obs.attrs["filename"][:4].upper()
        date = orbits.index.get_level_values('time')[0]
        date = str(date.date()).replace("-", "")
        
        FigureName = f"{station}_{time_system}_{date}"
        
        df.to_csv(f"Database/{FigureName}.txt", sep = " ", index = True)

        
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
    
