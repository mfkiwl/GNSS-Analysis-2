from gnss_utils import fname_attrs
import georinex as gr
from read_rinex import rinex

def test_filenames(filenames: list):
    
    f = "alar0011.22o"
    f1 = "igr21906.sp3"
    f2 = "CAS0MGXRAP_20220010000_01D_01D_DCB.BSX"            
    filenames = [f, f1, f2]
    
    for x in filenames:
        for y in filenames:
            assert fname_attrs(x).date == fname_attrs(y).date, "One file doesn match"
            


def test_compare_georinex(infile, prn = "R01"):
    infile = "database/rinex/2014/alar0011.14o"
    
    obs = gr.load(infile, useindicators = True)
    
    df = rinex(infile).obs
    
    df1 = obs.sel(sv =  prn).to_dataframe()
    df = df.loc[df["prn"] == prn]
    
    #df.index = df.time
    
    readRinex = df["L1"].dropna()
    geoRinex = df1["L1"].dropna()
    
    print(readRinex, geoRinex)
    #assert readRinex == geoRinex, "Are equals" 
    
#infile = "database/rinex/2014/alar0011.14o"

#test_compare_georinex(infile, prn = "R01")