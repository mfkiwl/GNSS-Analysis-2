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

    result = { "lon": [], "lat": []}
    
    out_times = []


    for num in range(len(times)):

        sat_x, sat_y, sat_z, time = sat_x_vals[num], sat_y_vals[num], sat_z_vals[num], times[num]

        ip = IonosphericPiercingPoint(sat_x, sat_y, sat_z, 
                                      obs_x, obs_y, obs_z)

        elevation = ip.elevation(lat, lon)

        lat_ip, lon_ip = ip.ionospheric_sub_point(lat, lon)

        if elevation > 0:

            result['lon'].append(lon_ip)
            result['lat'].append(lat_ip)
            out_times.append(time)

    return pd.DataFrame(result, index = out_times)


def relative_tec_data(filename, prn = "G01"):
    
    df = pd.read_csv(filename, 
                 delim_whitespace=(True), 
                 index_col = ["sv", "time"])
    
    ob = observables(df, prn = prn)

    # phases carriers
    l1_values = ob.l1
    l2_values = ob.l2

    # Loss Lock Indicator
    l1lli_values, l2lli_values = ob.l1lli, ob.l2lli

    # Pseudoranges
    c1_values, p2_values = ob.c1, ob.p2

    # time
    time = ob.time


    l1, l2, rtec = cycle_slip_corrector(time, l1_values, l2_values, 
                                            c1_values, p2_values, 
                                            l1lli_values, l2lli_values)
    rtec = relative_tec(time, c1_values, 
                        p2_values, rtec)


    return pd.DataFrame({"RTEC": rtec}, index = time)


def concataned(data_1, data_2 = None, 
               time_interpol = "10min"):
    
    df = pd.concat([data_1, data_2], axis = 1)
    
    if time_interpol:
        df = df.resample(time_interpol).asfreq().interpolate().ffill().bfill()
    
    return df



def example():
    # Example: Arapiraca (Brazil) positions
    obs_x, obs_y, obs_z = 5043729.726, -3753105.556, -1072967.067
    
    tec = relative_tec_data(filename, prn = "G01")
    
    ip = piercing_points_data("Database/jpl17733.sp3/", 
                          "igr17733.sp3", 
                          "G01", obs_x, obs_y, obs_z)