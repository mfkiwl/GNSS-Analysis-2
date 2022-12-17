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
            



infile = "database/rinex/2014/alar0011.14o"

df = rinex(infile).load()

obs = gr.load(infile, useindicators = True)

print(df)

#%%
prn = "G02"
df1 = obs.sel(sv =  prn).to_dataframe()

print(obs)