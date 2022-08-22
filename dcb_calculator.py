import os
import pandas as pd
from constants import constants as const


def find_header(infile:str,
                header: str = 'yyyy.MM.dd') -> tuple:

    """Function for find the header (string) and the data body"""

    with open(infile) as f:
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

    
def load_dcb(infile, filename = None):
    
    """GNSS Differential Code Bias (DCBs) """
    
    
    if filename == None:
        path = infile
    else:
        path = os.path.join(infile, filename)
    

    header, data = find_header(path, header = '+BIAS/SOLUTION')

    def _extract_elements(dat):
        BIAS = dat[:5].strip()
        version = dat[5:9].strip()
        file_agency = dat[9:13].strip()
        creation_time = dat[13:18].strip()
        code = dat[18:28].strip()

        return [BIAS, version, file_agency, 
                creation_time, code] + dat[28:].split()


    str_data =  [_extract_elements(num) for num in data]

    names = ["bias", "svn", "prn", "site", 
            "domes", "obs1", "obs2", "b_start", 
            "b_end", "unit", "value", "std"]


    df = pd.DataFrame(str_data, columns = names)

    df[["value", "std"]] = df[["value", "std"]].apply(pd.to_numeric, 
                                                      errors='coerce')
    
    df.drop(columns = ["b_start", "b_end", "bias", "unit"], inplace = True)

    return df





def sat_bias_corrector(infile, prn = "G01"):
    
    dcb = load_dcb(infile)

    value = float(dcb.loc[(dcb["obs2"] == "C2X") & 
                          (dcb["prn"] == prn ),  "value"])

    return ((-1 * value) * (const.c / pow(10, 9))) * const.factor_TEC
