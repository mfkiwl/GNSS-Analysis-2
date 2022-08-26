import gnsscal
import datetime
import numpy as np


def julian_to_date(jd):

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

day = datetime.date(2015, 5, 22)

week, number = gnsscal.date2gpswd(day)

year, doy = gnsscal.gpswd2yrdoy(week, number)

date = datetime.date(year, 1, 1) + datetime.timedelta(doy - 1)