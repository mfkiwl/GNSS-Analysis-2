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

        

def get_paths(year: int) -> tuple:
    
    tec = f"Database/process/{year}/"
    orbit = f"Database/orbit/{year}/"
    dcb = f"Database/dcb/{year}/"
    
    paths_out = []
    for path in [tec, orbit, dcb]:
        _, _, files = next(os.walk(path))
        path += files[0]
        paths_out.append(path)
    
    return tuple(paths_out)

year = 2022
path_tec, path_orbit, path_dcb = get_paths(year)
        