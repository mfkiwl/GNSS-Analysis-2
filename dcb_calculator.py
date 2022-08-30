import os
import pandas as pd
from constants import constants as const
import numpy as np

def find_element(data, header):
    """Find the header (like string) and the data body"""
    count = 0
    for num in range(len(data)):
        if (header) in data[num]:
            break
        else:
            count += 1
    return count



def separe_elements(dat: str) -> list:
    """Separe elements from each row in dcb file"""
    BIAS = dat[:5].strip()
    version = dat[5:9].strip()
    file_agency = dat[9:13].strip()
    creation_time = dat[13:18].strip()
    code = dat[18:28].strip()

    return [BIAS, version, file_agency, 
            creation_time, code] + dat[28:].split()


def load_dcb(infile: str) -> pd.DataFrame:
    """Pipeline of dcb into pandas dataframe"""
    
    with open(infile) as f:
        data = [line.strip() for line in f.readlines()]
    
    header = "*BIAS"
    count = find_element(data, header = header)
    header = [i.replace("_", "").lower() for i in data[count:][0].split()]
    
    data_result = []
    
    for element in data[count + 1:]:
    
        if "-BIAS" in element:
            break
        else:
            data_result.append(separe_elements(element)) 
    
    return pd.DataFrame(data_result, columns = header)



def get_cdb_value(infile, prn):
    """Get dcb value from obs combination"""
    df = load_dcb(infile)
    
    try:
        est_value = df.loc[(df["obs1"] == "C1W") & 
                     (df["obs2"] == "C2W") &
                     (df["prn"] == prn),  
                     "estimatedvalue"]    
        
        if len(est_value) == 0:
            value = 0
        else:
            value = float(est_value)
        
    except:
        
        est_value = df.loc[(df["obs1"] == "C2C") & 
                     (df["obs2"] == "C2W") &
                     (df["prn"] == prn),  
                     "estimatedvalue"]    
        
        value = float(est_value)
        
        if len(est_value) == 0:
            value = 0
        else:
            value = float(est_value)
        
        
        
    return ((-1 * value) * (const.c / pow(10, 9))) * const.factor_TEC
        
  
def create_prns(constellation:str = "G") -> list:
    
    """Create a prn list"""
    
    out = []    
    for num in range(1, 33):
        if num < 10:
            prn = f"{constellation}0{num}"
        else:
            prn = f"{constellation}{num}"
            
        out.append(prn)
        
    return out

infile = "Database/dcb/2015/CAS0MGXRAP_20151310000_01D_01D_DCB.BSX"

def test():
    
    for prn in create_prns():
        
        df = load_dcb(infile)
        
        value = get_cdb_value(infile, prn)
        
        
        print(f"{prn}: {value}")
    
