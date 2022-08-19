# -*- coding: utf-8 -*-
"""
Created on Tue Aug  9 10:24:16 2022

@author: Luiz
"""

import georinex as gr
import pandas as pd
import numpy as np

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

def load_orbits(orbital_path, prn = None):

    orbits = gr.load(orbital_path)

    if prn == None:
        orbits = orbits.to_dataframe()
    else:
        orbits = orbits.sel(sv = prn).to_dataframe()

    orbits.drop(columns = ["clock", "dclock", "velocity"], inplace = True)

    return orbits
    
    
def join(receiver_path, orbital_path, first = "orbit"):
     
    rinex = load_receiver(receiver_path)
    orbit = load_orbits(orbital_path)

    if first == "rinex":
        return rinex.join(orbit.reindex(orbit.index, level = 1))

    else:
        return orbit.join(rinex.reindex(rinex.index, level = 1))

def save():
        time_system = obs.attrs["time_system"]
        station = obs.attrs["filename"][:4].upper()
        date = orbits.index.get_level_values('time')[0]
        date = str(date.date()).replace("-", "")
        
        Filename = f"{station}_{time_system}_{date}"
        
        df.to_csv(f"Database/{Filename}.txt", sep = " ", index = True)


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
    
