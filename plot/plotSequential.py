from utils import doy_str_format
from ROTI import *
import matplotlib.dates as dates 
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

infile = "Database/all_process/2014/001_test/"

def plot_tec_rate(df, prn, station, save = False):
    
    if save:
        plt.ioff()
    
    df1 = df.loc[(df.el > 30) & (df.prn == prn), :]
    date = df1.index[0].strftime("%d/%m/%Y")
    time = df1.index
    stec = df1.stec.values
    
    
    title = f"{prn.upper()} ({station.upper()}) - {date}"
    
    fig, ax = plt.subplots(figsize = (10, 6), 
                           nrows = 4, 
                           sharex = True)
    
    plt.subplots_adjust(hspace = 0.0)
    
    

    args = dict(color = "k", lw = 1)
    ax[0].plot(df1.el, **args)
    ax[0].set(ylabel = "Elevation (°)", 
              title = title)

    ax[1].plot(time, stec, **args)
    ax[1].set(ylabel = "STEC (TECU)")
    
    #indexes = find_gaps(df1).gaps
    dtec = df1["stec"] - df1["stec"].rolling("2.5min").mean()
    rot, rot_time, roti, roti_time = rot_and_roti(dtec, time)
    #rtime, rot = func_rot(stec, time)
    #drot = rot - running(rot)

    ax[2].plot(rot_time, rot, **args)
    ax[2].set(ylabel = "ROT")

    #roti_time, roti_values = func_roti(rtime, drot, step = 4, length = 1)
    ax[3].plot(roti_time, roti, **args)


    delta_lim = timedelta(hours = 2)
    ax[3].set(ylabel = "ROTI \n (TECU/min)", 
              ylim = [0, 5], 
              xlim = [df1.index[0] - delta_lim, 
                      df1.index[-1] + delta_lim], 
              xlabel = "time (UT)")

    ax[3].xaxis.set_major_formatter(dates.DateFormatter('%H'))
    ax[3].xaxis.set_major_locator(dates.HourLocator(interval = 1))
    
    plt.rcParams.update({'font.size': 12})  
    if save:
        print("Saving...", prn)
        fig.savefig(f"img/roti/{station}/{prn}.png", 
                   dpi = 100, facecolor="white", transparent=False)
        
        plt.clf()   
        plt.close()
    else:
        plt.show()
        
        
station = filename.replace(".txt", "")

df = pd.read_csv(infile + filename, 
         delim_whitespace = True, 
         index_col = "time")

df.index = pd.to_datetime(df.index)
plot_tec_rate(df, prn, station, save = False)