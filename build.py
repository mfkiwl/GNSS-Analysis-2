import sys
from utils import *
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
        return os.path.join(self.current_path, "orbit", self.const)
      
    @property
    def fn_orbit(self):
        fname = f"igr{self.week}{self.number}.sp3"
        return os.path.join(self.orbit, fname)
    
    @property
    def rinex(self):
        return os.path.join(self.current_path, "rinex", 
                            self.year, self.doy)
    
    def fn_rinex(self, station):
        fname = f"{station}{self.doy}1.14o"
        return os.path.join(self.rinex, fname)
    
    def process(self, _all = True):
        if _all:
            return os.path.join(self.current_path, "all_process")
        else:
            return os.path.join(self.current_path, "process")
        
    def fn_process(self, _all = True):
        fname =  f"{station}.txt"
        return  os.path.join(process(_all = _all), fname)
        
    def json(self, fname = "stations.json"):
        return os.path.join(self.current_path, "json", fname)
    
    
def main():
    
    year = 2014
    doy = 1

       
    path = build_paths(year, doy)
    
    print(path.process(_all = False))
    
    
main()
    
    