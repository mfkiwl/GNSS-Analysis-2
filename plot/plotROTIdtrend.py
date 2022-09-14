import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as dates
from ROTI import rot_and_roti
import datetime
from __init__ import *
 
infile = "Database/all_process/2015/mgbh/mgbh131.txt"

df = pd.read_csv(infile, delim_whitespace = True, index_col = "time")

df.index = pd.to_datetime(df.index)



def plotdTrendComparation(df, prn = "G02", save = False, 
                          ncols = 4, nrows = 2):
    
    
    fig, ax = plt.subplots(figsize = (5*ncols, 4*nrows), 
                           nrows = nrows, 
                           ncols = ncols, 
                           sharex = True)

    plt.subplots_adjust(hspace = 0)

    df = df.loc[(df.prn == prn) & (df.el > 30), :]
    
    time = df.index
    
    for num in range(ncols):
        
        delta = 2.5 * num 
        if num == 0:
            dtec = df.stec.values
            title = "Dados brutos"
            
        else:
            title = f'dTrend {delta} min'
            dtec = df["stec"] - df["stec"].rolling(title.replace("dTrend ", "")).mean()
            
        rot, rot_time, roti, roti_time = rot_and_roti(dtec, time)
        ax[0, num].plot(rot_time, rot)
        ax[1, num].plot(roti_time, roti)
        
        ax[0, num].set(ylabel = "ROT", title = title, 
                       ylim = [-5, 5])
        
        ax[1, num].set(ylabel = "ROTI",  ylim = [0, 3], xlabel = "Tempo (UT)")
    
    
    ax[1, 1].set(ylabel = "ROTI",  ylim = [0, 3],  
                 xlabel = "Tempo (UT)")
    
    #
    
    
    for ax in ax.flatten():
        ax.axhline(0, color = "k", linestyle = "--")
        ax.xaxis.set_major_formatter(dates.DateFormatter('%H:%M'))
        ax.xaxis.set_major_locator(dates.HourLocator(interval = 1))
    
    date = df.index[0].date()
    
    fig.suptitle(f"{station} - {prn} - {date}")
    
    if save:
        filename  = f"{prn}_{str(date).replace('-', '')}"
        
        fig.savefig(f'img/roti/{filename}.png', 
                    dpi = 100,
                    bbox_inches="tight")


#plotdTrendComparation(df, prn = "G02", save = True, 
#                          ncols = 5, nrows = 2)


def plotFilterTime(df, prn = "G02", save = False):
    
    fig, ax = plt.subplots(figsize = (14, 10), 
                           nrows = 2,
                           sharex = True)
    
    plt.subplots_adjust(hspace = 0)
    
    df = df.loc[(df.prn == prn) & (df.el > 30), :]

    for num in range(5):
        
        delta = 2.5 * num 
        if num == 0:
            dtec = df.stec.values
            title = "Dados brutos"
            
        else:
            title = f'dTrend {delta} min'
            dtec = df["stec"] - df["stec"].rolling(title.replace("dTrend ", "")).mean()
            
        rot, rot_time, roti, roti_time = rot_and_roti(dtec, time)
        ax[0].plot(rot_time, rot)
        ax[1].plot(roti_time, roti, label = title)
        
    ax[1].legend(ncol = 3)
        
        
    ax[0].set(ylabel = "ROT", title = f"{station} - {prn} - {date}", 
                   ylim = [-5, 5])
    
    ax[1].set(ylabel = "ROTI",  ylim = [0, 3], 
              xlim = [datetime.datetime(2015, 5, 11, 7, 0), 
                      datetime.datetime(2015, 5, 11, 8, 0)],
              xlabel = "Tempo (UT)")
    
    
    for ax in ax.flatten():
        ax.axhline(0, color = "k", linestyle = "--")
        ax.xaxis.set_major_formatter(dates.DateFormatter('%H:%M'))
        ax.xaxis.set_major_locator(dates.MinuteLocator(interval = 10))
        
        
    if save:
        filename  = f"{prn}_{str(date).replace('-', '')}_overlap"
        
        fig.savefig(f'img/roti/{filename}.png', 
                    dpi = 500,
                    bbox_inches="tight")
plotFilterTime(df, prn = "G02", save = True)