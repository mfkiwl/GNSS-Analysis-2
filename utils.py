import gnsscal
import datetime
import numpy as np
import os

def julian_to_date(jd:float) -> datetime.datetime:
    
    """Convert julian date to datetime format"""

    jd = jd + 0.5
    F, I = np.modf(jd)
    I = int(I)
    A = np.trunc((I - 1867216.25) / 36524.25)

    if I > 2299160:
        B = I + 1 + A - np.trunc(A / 4.)
    else:
        B = I

    C = B + 1524

    D = np.trunc((C - 122.1) / 365.25)

    E = np.trunc(365.25 * D)

    G = np.trunc((C - E) / 30.6001)

    day = C - E + F - np.trunc(30.6001 * G)

    if G < 13.5:
        month = G - 1
    else:
        month = G - 13

    if month > 2.5:
        year = D - 4716
    else:
        year = D - 4715

    days, day = np.modf(day)

    day = int(day)

    hours = days * 24.
    hours, hour = np.modf(hours)

    mins = hours * 60.
    mins, minute = np.modf(mins)

    secs = mins * 60.
    secs, sec = np.modf(secs)
    
    micro = round(secs * 1e6)
    
    if sec < 30.0:
        
        sec = sec + round(secs)
    elif sec == 59.0:
        sec = 0
        minute = minute + 1
        if minute == 60:
            minute = 0 
                
   
    return datetime.datetime(int(year), int(month), int(day),
                             int(hour), int(minute), int(sec))



        

#date = datetime.date(year, month, day)

def gpsweek_from_date(date: datetime.datetime) -> tuple:
    
    """Return GPS week and number from date"""

    return gnsscal.date2gpswd(date)

def doy_from_gpsweek(week: int, number: int) -> tuple:
    
    """Return year and doy from gps week"""

    return gnsscal.gpswd2yrdoy(week, number)

def date_from_doy(year: int, doy:int):
    
    """Return date from year and doy"""

    return datetime.date(year, 1, 1) + datetime.timedelta(doy - 1)

        

def get_paths(year: int, station: str) -> tuple:
    
    tec = f"Database/rinex/{year}/{station}/"
    orbit = f"Database/orbit/{year}/igr/"
    dcb = f"Database/dcb/{year}/"
    
    paths_out = []
    for path in [tec, orbit, dcb]:
        
        _, _, files = next(os.walk(path))

        for filename in files: 
            
            last_str = filename[-1] 
            
            rules = [last_str == "o", 
                     last_str == "3",
                     last_str == "X"]
            
            if any(rules):
                path += filename

        paths_out.append(path)
        
    return tuple(paths_out)


year = 2015
path_tec, path_orbit, path_dcb = get_paths(year)

print(path_tec, path_orbit, path_dcb)


class fname_attrs(object):
    
    """Attributes of filenames (rinex, orbit and bias)"""
    
    def __init__(self, fname):
        
        extension = fname.split(".")
        if extension[1][-1] == "o":
        
            self.station = extension[0][:4]
            year = extension[1][:2]
            doy = extension[0][4:7]

            if int(year) < 99:
                year = "20" + year
            else:
                year = "19" + year

            self.year = int(year)
            self.doy = int(doy)
            
        elif extension[1] == "sp3":
            
            self.const = extension[0][:3]
            week = int(extension[0][3:7])
            number = int(extension[0][7:])
            
            self.year, self.doy = doy_from_gpsweek(week, number)
            
        else:
            args = extension[0].split("_")

            if "MGX" in args[0]:
                self.year = int(args[1][:4])
                self.doy = int(args[1][4:7])
                
                
        self.date = date_from_doy(self.year, self.doy)
         
    
  

def main():
    f = "alar0011.22o"
    f1 = "igr21906.sp3"
    f2 = "CAS0MGXRAP_20220010000_01D_01D_DCB.BSX"
    
    
    for x in [f, f1, f2]:
        for y in [f, f1, f2]:
            print(fname_attrs(x).date, fname_attrs(y).date)
            
            
#main()