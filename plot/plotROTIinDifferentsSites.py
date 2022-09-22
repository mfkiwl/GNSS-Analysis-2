from plot.plotConfig import *
import pandas as pd
from ROTI import rot_and_roti
from plot.plotStations import get_coords_from_sites



year = 2014
doy = 1 

def date_to_decimal(date):
    return date.hour + (date.minute / 60) + (date.second / 3600)
    



def pipeline(infile, elevation = 30):

    df = pd.read_csv(infile, delim_whitespace = True, index_col = "time")
    df.index = pd.to_datetime(df.index)
        
    
    out_roti = []
    out_time = []  
    
    for prn in np.unique(df.prn.values):
        
        df1 = df.loc[(df.prn == prn) & (df.el > elevation), :]
        
        stec = df1["stec"].values
        time = df1.index
    
        rot, rot_tstamps, roti, roti_tstamps = rot_and_roti(stec, time)
        
        out_roti.extend(roti)
        
        time = np.array([date_to_decimal(f) for f in roti_tstamps])
    
        out_time.extend(time)
        
        
    roti = np.array(out_roti)
    time = np.array(out_time)
    
    return time, roti
    
    


def secondary_axis(ax, delta = - 3):
    """Adding an secondory axis for show time in LT"""
    ax1 = ax.twiny()
    
    ax1.set(xticks = ax.get_xticks(), 
            xlabel = "Time (LT)", 
            xlim = ax.get_xlim())
    
    def rate(x, delta = -3):
        if (x > 0):
            return f"{x + delta}"
        else:
            return f"{24 + delta}"
    
    ax1.xaxis.set_major_formatter(lambda x, pos: rate(x, delta = delta))
    
    ax1.xaxis.set_ticks_position('bottom') 
    ax1.xaxis.set_label_position('bottom') 
    ax1.spines['bottom'].set_position(('outward', 45))   
    
path_json = f'Database/json/{year}/001.json'

dat = json.load(open(path_json))

    
stations = ["recf", "alar", "pbjp", "rnna", "ceft"]
stations = stations[::-1]

fig, ax = plt.subplots(figsize = (10, 15), 
                       nrows = len(stations), 
                       sharex = True)

plt.subplots_adjust(hspace = 0)

for num, ax in enumerate(ax.flat):
    
    station = stations[num]
    
    infile = f"Database/all_process/2014/001_test/{station}.txt"
    
    time, roti = pipeline(infile, elevation = 30)
    
    lon, lat = get_coords_from_sites(dat, station)
    
    ax.plot(time, roti, marker = "o", markersize = 1, 
            linestyle = "none", color = "k", label = station.upper())
        
    ax.text(10, 4, f"{station.upper()} ({round(lat, 2)}°,{round(lon, 2)}°)", 
            transform = ax.transData)
    
    ax.set(ylabel = "ROTI (TECU/min)", 
           xlabel = "Time (UT)", 
           xticks = np.arange(0, 25, 3), 
           xlim = [0, 24], ylim = [0, 5])
    
    if num == 4:
        secondary_axis(ax, delta = - 3)
    
    if num == 0:
        ax.set_title("01 January 2014")
