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

        dcb = pd.DataFrame(data_result, columns = header)
        
        date = infile.split("_")[1]
        
        if int(date[:4]) == 2015:
            obs1 = "C2C"
        else:
            obs1 = "C1C"
        

        est_value = dcb.loc[(dcb["obs1"] == obs1) &
                             (dcb["obs2"] == "C2W") &
                             (dcb["prn"] == prn),  "estimatedvalue"]

        self.value = float(est_value)

        self.value_tec = ((-1 * self.value) * 
                          (const.c / pow(10, 9))) * const.factor_TEC
                          
        @property                  
        def data(self):
            return dcb
        
        


def main():
    infile = "Database/dcb/2015/CAS0MGXRAP_20151310000_01D_01D_DCB.BSX"
    #filename = "CAS0MGXRAP_20220010000_01D_01D_DCB.BSX"
   
    prn = "G01"
    df = load_dcb(infile , prn = prn).value_tec   
   
    print(df)
#main()

