from utils import *

def test_filenames(filenames: list):
    
    for x in filenames:
        for y in filenames:
            assert fname_attrs(x).date == fname_attrs(y).date, "One file doesn match"
            


if __name__ == "__main__":
    f = "alar0011.22o"
    f1 = "igr21906.sp3"
    f2 = "CAS0MGXRAP_20220010000_01D_01D_DCB.BSX"            
    filenames = [f, f1, f2]
    test_filenames(filenames)
    print("Filenames date passed")