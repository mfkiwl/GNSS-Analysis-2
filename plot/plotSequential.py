from rot_roti import rot, roti
import matplotlib.dates as dates 
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from plotConfig import *
import datetime 
from build import tex_path

def plotSequetialParameters(df, prn, ncol, ax):
    
    """Plotting subplots for each TEC rate and slant TEC"""
    
    df1 = df.loc[(df.el > 30) & (df.prn == prn), :]    
    if prn == "G18":
        df1 = df1.loc[df1.index < datetime.datetime(2014, 1, 1, 4, 0)]
        title = f"PRN = {prn.upper()} (com bolha)"
    else:
        title = f"PRN = {prn.upper()} (sem bolha)"
        
    
    df1 = df1.dropna()
    time = df1.index
    stec = df1.stec.values

    
    args = dict(color = "k", lw = 2)
    ax[0, ncol].plot(df1.el, **args)
    ax[0, ncol].set(ylabel = "Elevação (°)", 
                    title = title, 
                    ylim = [30, 90], 
                    yticks = np.arange(20, 100, 20))

    ax[1, ncol].plot(time, stec, **args)
    ax[1, ncol].set(ylabel = "STEC (TECU)", 
              ylim = [-20, 40])

    rot_time, vrot = rot(stec, time)
    roti_time, vroti = roti(stec, time)
   

    ax[2, ncol].plot(rot_time, vrot, **args)
    ax[2, ncol].set(ylabel = "ROT (TECU/min)", 
              ylim = [-12, 12], 
              yticks = np.arange(-10, 12, 5))
    

    ax[3, ncol].plot(roti_time, vroti, **args)


    ax[3, ncol].set(ylabel = "ROTI (TECU/min)", 
              ylim = [0, 6], 
              yticks = np.arange(0, 6, 1),
              xlabel = "Hora universal (UT)")

    ax[3, ncol].xaxis.set_major_formatter(dates.DateFormatter('%H'))
    ax[3, ncol].xaxis.set_major_locator(dates.HourLocator(interval = 1))
    

        
def main():
    infile = "database/examples/"
    filename = "without_with_epbs.txt"

    df = pd.read_csv(infile + filename,
                     index_col = 0)
    
    df.index = pd.to_datetime(df.index)
    date = df.index[0].strftime("%d de %B de %Y")
    
    fig, ax = plt.subplots(figsize = (30, 30), 
                          nrows = 4,
                          ncols = 2, 
                          sharex='col')
    plt.subplots_adjust(hspace = 0.0)
    
    station = "pbjp"
    
    for ncol, prn in enumerate(["G02", "G18"]):
        plotSequetialParameters(df, prn, ncol, ax)
        
    fig.suptitle(f"Estação: {station.upper()} - {date}", 
                 y = 0.95)
    
    
    path_to_save = os.path.join(tex_path("methods"), 
                                "sequential_parameters.png")
    #print(path_to_save)

    fig.savefig(path_to_save ,
                dpi = 300
                )
    
