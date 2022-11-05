import matplotlib.pyplot as plt
import pyIGRF
import numpy as np
import pandas as pd
import cartopy.crs as ccrs
from build import paths

year = 2014.
def run_magnetic_data(year, step = 1):
    out = []
    for lat in np.arange(-90, 90 + step, step):
        for lon in np.arange(-180, 180 + step, step):
            d, i, h, x, y, z, f = pyIGRF.igrf_value(lat, lon, 
                                                    alt=0., 
                                                    year= year)
            
            out.append([lat, lon, d, i])
            
    return pd.DataFrame(out, columns = ["lat", "lon", "d", "i"])
 

     


def save(year):
    eq = run_magnetic_data(year, step = 1)
    eq = pd.pivot_table(eq, 
                        columns = "lon", 
                        index = "lat", 
                        values = "i")
    eq.to_csv(paths(int(year)).geo, 
                sep = ",",
                index = True, 
                header = True)

