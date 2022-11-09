from __future__ import (absolute_import, division, print_function)

import cmath
import numpy as np
from numpy import ma
from astropy.time import Time
from scipy import interpolate


def JulianDayFromDate(date, calendar='standard'):
    """
creates a Julian Day from a 'datetime-like' object.  Returns the fractional
Julian Day (resolution 1 second).

if calendar='standard' or 'gregorian' (default), Julian day follows Julian 
Calendar on and before 1582-10-5, Gregorian calendar after 1582-10-15.

if calendar='proleptic_gregorian', Julian Day follows gregorian calendar.

if calendar='julian', Julian Day follows julian calendar.

Algorithm:

Meeus, Jean (1998) Astronomical Algorithms (2nd Edition). Willmann-Bell,
Virginia. p. 63
    """
    # based on redate.py by David Finlayson.
    year = date.year
    month = date.month
    day = date.day
    hour = date.hour
    minute = date.minute
    second = date.second
    # Convert time to fractions of a day
    day = day + hour/24.0 + minute/1440.0 + second/86400.0
    # Start Meeus algorithm (variables are in his notation)
    if (month < 3):
        month = month + 12
        year = year - 1
    A = int(year/100)
    jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + \
        day - 1524.5
    # optionally adjust the jd for the switch from
    # the Julian to Gregorian Calendar
    # here assumed to have occurred the day after 1582 October 4
    if calendar in ['standard', 'gregorian']:
        if jd >= 2299170.5:
            # 1582 October 15 (Gregorian Calendar)
            B = 2 - A + int(A/4)
        elif jd < 2299160.5:
            # 1582 October 5 (Julian Calendar)
            B = 0
        else:
            raise ValueError(
                'impossible date (falls in gap between end of Julian calendar and beginning of Gregorian calendar')
    elif calendar == 'proleptic_gregorian':
        B = 2 - A + int(A/4)
    elif calendar == 'julian':
        B = 0
    else:
        raise ValueError(
            'unknown calendar, must be one of julian,standard,gregorian,proleptic_gregorian, got %s' % calendar)
    # adjust for Julian calendar if necessary
    jd = jd + B
    return jd

def epem(date):
    """
    input: date - datetime object (assumed UTC)
    ouput: gha - Greenwich hour angle, the angle between the Greenwich
           meridian and the meridian containing the subsolar point.
           dec - solar declination.
    """
    dg2rad = np.pi/180.
    rad2dg = 1./dg2rad
    # compute julian day from UTC datetime object.
    # datetime objects use proleptic gregorian calendar.
    jday = JulianDayFromDate(date, calendar='proleptic_gregorian')
    jd = np.floor(jday)  # truncate to integer.
    # utc hour.
    ut = date.hour + date.minute/60. + date.second/3600.
    # calculate number of centuries from J2000
    t = (jd + (ut/24.) - 2451545.0) / 36525.
    # mean longitude corrected for aberration
    l = (280.460 + 36000.770 * t) % 360 
    # mean anomaly
    g = 357.528 + 35999.050 * t 
    # Eccentricity
    e = 0.01675104 - 0.0000418 * t  - 0.000000126 * t**2 
    # Sun's equation of center
    c = (1.919460 - 0.004789 * t - 0.000014 * t**2) * np.sin(g/rad2dg) 
    + (0.020094 - 0.000100*t) * np.sin(2*g/rad2dg) 
    + 0.000293*np.sin(3*g/rad2dg)
    # Sun's true anomaly (deg)
    ta = (g + c) % 360
    # Sun's radius vector
    dist = 1.0000002*(1. - e**2)/(1. + e*np.cos(ta/rad2dg))
    # ecliptic longitude
    lm = l + 1.915 * np.sin(g*dg2rad) + 0.020 * np.sin(2*g*dg2rad)
    # obliquity of the ecliptic
    ep = 23.4393 - 0.01300 * t
    # equation of time
    eqtime = -1.915*np.sin(g*dg2rad) - 0.020*np.sin(2*g*dg2rad) \
        + 2.466*np.sin(2*lm*dg2rad) - 0.053*np.sin(4*lm*dg2rad)
    # Greenwich hour angle
    gha = 15*ut - 180 + eqtime
    # declination of sun
    dec = np.arcsin(np.sin(ep*dg2rad) * np.sin(lm*dg2rad)) * rad2dg
    # apparent right accession.
    true_long = (l + c) % 360
    omega = 259.18 - 1934.142 * t
    app_long = true_long - 0.00569 - 0.00479 * np.sin(omega/rad2dg)
    ob1 = 23.452294 - 0.0130125 * t - 0.00000164 * t**2 + 0.000000503 * t**3
    ob2 = ob1 + 0.00256 * np.cos(omega/rad2dg)
    x = np.cos(app_long/rad2dg)
    y = np.cos(ob2/rad2dg) * np.sin(app_long/rad2dg)
    input_num = complex(x, y)
    r, phi = cmath.polar(input_num)
    app_ra = phi  * rad2dg
    app_ra = app_ra + 360 if app_ra < 0. else app_ra
    app_ra = app_ra/15
    return app_ra, dec, dist

def terminator(date, TwilightAngle):

    dg2rad = np.pi/180.

    earthRadius = 6.371009e6
    ra, sun_lat, sun_distance = epem(date)
    t = Time(date.strftime("%Y-%m-%d %H:%M:%S%Z"), scale='utc')
    lm_sidereal_time = np.array(t.sidereal_time('apparent', 'greenwich'))

    sun_lon = 15.0 * (ra - lm_sidereal_time)
    scanAngle = np.arcsin((earthRadius / (sun_distance * 1.4956e11)) * np.sin(1.25663706))
    arc_dist = np.pi - 1.57080 - scanAngle + TwilightAngle * 0.017453295
    cdist = np.cos(arc_dist)		
    sdist = np.sin(arc_dist)

    lon_terminus = []
    lat_terminus = []
    for j in range(36):
        count = j
        azimuth =  count * 10.0
        az = azimuth * dg2rad
        sinll1 = np.sin(sun_lat * dg2rad)
        cosll1 = np.cos(sun_lat * dg2rad)

        phi = np.arcsin(sinll1 * cdist + cosll1 * sdist * np.cos(az))
        lam = (sun_lon * dg2rad) + np.arctan2(sdist * np.sin(az), cosll1*cdist - sinll1 * sdist * np.cos(az))

        while lam < -np.pi: lam = lam + 2 * np.pi
        while lam > np.pi: lam = lam - 2 * np.pi

        center_lon = 0.0
        lon_terminus.append((lam/dg2rad) + center_lon)
        lat_terminus.append(phi/dg2rad)

    # tck, u = interpolate.splprep([lon_terminus, lat_terminus], s=0, per=True)
    # lon_terminus, lat_terminus = interpolate.splev(np.linspace(0, 1, 100), tck)

    # zipped_lists = zip(lon_terminus, lat_terminus)
    # sorted_pairs = sorted(zipped_lists)

    # tuples = zip(*sorted_pairs)
    # lon_terminus, lat_terminus = [list(tuple) for tuple in  tuples]

    delta_mask_lon = lon_terminus - np.roll(lon_terminus, -1)        
    delta_mask_lat = lat_terminus - np.roll(lat_terminus, -1)        
    
    id_lon = np.where(abs(delta_mask_lon) > 180.)
    id_lat = np.where(abs(delta_mask_lat) > 90.)

    mc_lon = ma.array(lon_terminus)
    mc_lat = ma.array(lat_terminus)
    if id_lon:
        mc_lon[id_lon] = ma.masked
    if id_lat:
        mc_lat[id_lat] = ma.masked
    
    
    
    
    
    # delta_mask = lon_terminus - np.roll(lat_terminus, -1)        
    # id = np.where(abs(delta_mask) > 180.)

    # mc = ma.array(lat_terminus)
    # mc[id] = ma.masked

    # return lon_terminus, mc
    return mc_lon, mc_lat
    # return lon_terminus, lat_terminus
