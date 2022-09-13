import sys
from utils import *
import os
os.path.dirname(sys.executable)
from pathlib import Path



class build_paths(object):
    
    def __init__(self, year: int, doy: int, const: str = "igr"):
        
        """Construct paths from input values"""
        
        self.const = const
        
        self.date = date_from_doy(year, doy)
        self.week, self.number = gpsweek_from_date(self.date)
        
        self.current_path = os.path.join(str(Path.cwd()), "Database")
        
        self.year = str(year)
        self.doy = doy_str_format(doy)
    
    @property
    def orbit(self):
        return os.path.join(self.current_path, "orbit", self.doy)
     
    @property
    def rinex(self):
        return os.path.join(self.current_path, "rinex", 
                            self.year, self.doy)
    @property
    def process(self):
        return os.path.join(self.current_path, "process", 
                            self.year, self.doy)
    @property
    def all_process(self):
        return os.path.join(self.current_path, "all_process", 
                            self.year, self.doy)
    @property
    def dcb(self):
        return os.path.join(self.current_path, "dcb", self.year)
    
    def fn_process(self, station = "alar"):
        fname =  f"{station}.txt"
        return  os.path.join(self.process, fname)

    def fn_all_process(self, station = "alar"):
        fname =  f"{station}.txt"
        return  os.path.join(self.all_process, fname)
    
    def fn_orbit(self):
        fname = f"{self.const}{self.week}{self.number}.sp3"
        return os.path.join(self.orbit, fname)
    
    def fn_rinex(self, station, extension = "14o"):
        fname = f"{station}{self.doy}1.{extension}"
        return os.path.join(self.rinex, fname)
    
    def fn_dcb(self, mgx = True):
        if mgx:
            fname = f"CAS0MGXRAP_{self.year}{self.doy}0000_01D_01D_DCB.BSX" 
            return os.path.join(self.dcb, fname)
        
    def json(self, fname = "stations.json"):
        return os.path.join(self.current_path, "json", fname)
    

    
def main():
    
    year = 2022
    doy = 1

       
    path = build_paths(year, doy)
    
    #print(path.fn_process("vico"))
    
#main()
    
    