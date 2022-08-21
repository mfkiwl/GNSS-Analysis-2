from constants import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
from load import *

class observables(object):
    
    def __init__(self, df, prn = None):
        
        self.df = df 
        self.prns = np.unique(self.df.index.get_level_values('sv').values)
        
        if prn is not None:
            obs = self.df.loc[self.df.index.get_level_values('sv') == prn, :]
        else:
            obs = self.df
    
        self.l1 = obs.L1.values
        self.l2 = obs.L2.values
        self.c1 = obs.C1.values
        self.p2 = obs.P2.values
        
        self.l1lli = obs.L1lli.values.astype(int)
        self.l2lli = obs.L2lli.values.astype(int)
        
        self.time = pd.to_datetime(obs.index.get_level_values('time'))
        
def piercing_points_data(infile, 
                         filename, 
                         prn, 
                         obs_x, obs_y, obs_z):

    ob = load_orbits(infile, 
                     filename, 
                     prn = prn)

    sat_x_vals = ob.position("x").values.ravel()
    sat_y_vals = ob.position("y").values.ravel()
    sat_z_vals = ob.position("z").values.ravel()

    times = ob.position("x").index

    lon, lat, alt = convert_coords(obs_x, obs_y, obs_z)

    result = { "lon": [], "lat": [], "time": []}


    for num in range(len(times)):

        sat_x, sat_y, sat_z, time = sat_x_vals[num], sat_y_vals[num], sat_z_vals[num], times[num]

        ip = IonosphericPiercingPoint(sat_x, sat_y, sat_z, 
                                      obs_x, obs_y, obs_z)

        elevation = ip.elevation(lat, lon)

        lat_ip, lon_ip = ip.ionospheric_sub_point(lat, lon)

        if elevation > 0:

            result['lon'].append(lon_ip)
            result['lat'].append(lat_ip)
            result['time'].append(time)

    ip = pd.DataFrame(result)

    ip.index = ip.time

    del ip["time"]

    return ip

