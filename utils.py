import gnsscal
import datetime
import numpy as np
import os

def julian_to_date(jd: float) -> datetime.datetime:
    
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


def gpsweek_from_date(date: datetime.datetime) -> tuple:
    """Return GPS week and number from date"""
    return gnsscal.date2gpswd(date)

def doy_from_gpsweek(week: int, number: int) -> tuple:
    """Return year and doy from gps week"""
    return gnsscal.gpswd2yrdoy(week, number)

def date_from_doy(year: int, doy:int) -> datetime.datetime:
    """Return date from year and doy"""
    return datetime.date(year, 1, 1) + datetime.timedelta(doy - 1)

        

def create_prns(constellation: str = "G") -> list:
    
    """Create a prn list"""
    
    out = []    
    for num in range(1, 33):
        if num < 10:
            prn = f"{constellation}0{num}"
        else:
            prn = f"{constellation}{num}"
            
        out.append(prn)
        
    return out

def create_directory(path_to_create: str):
    """Create a new directory by path must be there year and doy"""
    try:
        os.mkdir(path_to_create)
        print(f"Creation of the directory {path_to_create} successfully")
    except OSError:
        print(f"Creation of the directory {path_to_create} failed")
    
    return path_to_create

def doy_str_format(date: int) -> str:
    """Convert integer to string. Ex: 1 to 001"""
    
    if isinstance(date, datetime.datetime):
        doy = date.timetuple().tm_yday
    else:
        doy = date
    
    if doy < 10:
        str_doy = f"00{doy}"
        
    elif doy >= 10 and doy < 100:
        str_doy = f"0{doy}"

    else:
        str_doy = f"{doy}"
        
    return  str_doy

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
         
    
  
