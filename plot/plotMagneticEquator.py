import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import cartopy.feature as cf
import cartopy.crs as ccrs
from plot.plotConfig import *
from scipy import interpolate
import pyIGRF
import datetime
import time


 


def toCoordFraction(degrees, minutes, seconds):
    if degrees > 0:
        return degrees + (minutes / 60) + (seconds / 3600)
    else:
        return degrees - (minutes / 60) - (seconds / 3600)
    

def toYearFraction(date):
    
    def sinceEpoch(date): # returns seconds since epoch
        return time.mktime(date.timetuple())
    s = sinceEpoch

    year = date.year
    startOfThisYear = datetime.datetime(year=year, month=1, day=1)
    startOfNextYear = datetime.datetime(year=year+1, month=1, day=1)

    yearElapsed = s(date) - s(startOfThisYear)
    yearDuration = s(startOfNextYear) - s(startOfThisYear)
    fraction = yearElapsed/yearDuration

    return date.year + fraction

def table_igrf(date = datetime.date(2010, 1, 1)):
    RT = 6370
    longitudes = np.arange(-180, 180, 1)
    latitudes  = np.arange(-90, 90, 1)

    #2010 and 2021
    date_fraction = toYearFraction(date)

    data = []

    for lon in longitudes:
        for lat in latitudes:
            D,I,H,X,Y,Z,F = pyIGRF.igrf_value(lat, lon, 0, date_fraction)
            data.append([lon, lat, I])
            
    df = pd.DataFrame(data, columns = ['Lon', 'Lat', 'Dip'])
    
    return pd.pivot_table(df, values='Dip', index=['Lat'], columns=['Lon'])

def run_and_save():
    table = np.rad2deg(np.arctan(np.tan(np.deg2rad(table)) * 0.5))

    table = table_igrf(datetime.datetime(2014, 1, 1))

    table.to_csv("Database/geo/Inclination2014.txt")

def plot_equator(ax):
    df = pd.read_csv("Database/geo/Inclination2021.txt", 
                     delimiter = ",", index_col = "Lat")
    
    ax.contour(df.columns, df.index, df.values, 1, 
               linewidths = 2,
                transform = ccrs.PlateCarree())

