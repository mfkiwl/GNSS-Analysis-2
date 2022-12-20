from gnss_utils import fname_attrs
from read_rinex import rinex
from load import load_receiver

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
    
    df1 = load_receiver(infile).df
    df = rinex(infile).obs
    
    prn = "R01"
    df1 = df1.loc[df1.index.get_level_values("sv") == prn]
    df = df.loc[df["prn"] == prn]
    
    mine = df["L1"].dropna().values
    geo = df1["L1"].dropna().values

    assert all(mine == geo), "No equals" 
    
