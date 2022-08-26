import os
import pandas as pd
from constants import constants as const


def find_element(data, header):
    
    """Find the header (like string) and the data body"""
    count = 0
    for num in range(len(data)):
        if (header) in data[num]:
            break
        else:
            count += 1
    return count



def separe_elements(dat):
    BIAS = dat[:5].strip()
    version = dat[5:9].strip()
    file_agency = dat[9:13].strip()
    creation_time = dat[13:18].strip()
    code = dat[18:28].strip()

    return [BIAS, version, file_agency, 
            creation_time, code] + dat[28:].split()

class load_dcb(object):
    
    """Load and getting GNSS Differential Code Bias (DCBs) value"""
    
    def __init__(self, infile, prn = "G01"):
        
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

        self.dcb = pd.DataFrame(data_result, columns = header)
        
        #if prn[0] == "G":
         #   receiver_type = "C2W"


        value = self.dcb.loc[(self.dcb["obs1"] == "C1C") & 
                             (self.dcb["obs2"] == "C2W") &
                             (self.dcb["prn"] == prn),  "estimatedvalue"]


        self.value = float(value)

        self.value_tec = ((-1 * self.value) * 
                          (const.c / pow(10, 9))) * const.factor_TEC
        
        


def main():
    infile = "Database/dcb/2022/"
    filename = "CAS0MGXRAP_20220010000_01D_01D_DCB.BSX"
    #bias = load_dcb(infile)
    
    df = load_dcb(infile + filename).value_tec
    #print(df.loc[df.prn == "G01", ["prn", "estimatedvalue", "obs1", "obs2"]])
    print(df)
main()

