from ROTI import *
import matplotlib.dates as dates 
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime 

infile = "Database/all_process/2014/001_test/"

def plot_tec_rate(df, prn, station, 
                  save = False, 
                  path_to_save = None):
    
    """Plotting subplots for each TEC rate and slant TEC"""
    
    if save:
        plt.ioff()
    
    df1 = df.loc[(df.el > 30) & (df.prn == prn), :]
    date = df1.index[0].strftime("%d/%m/%Y")
    time = df1.index
    stec = df1.stec.values
    
    
    title = f"{station.upper()} (PRN = {prn.upper()}) - {date}"
    
    fig, ax = plt.subplots(figsize = (6, 8), 
                           nrows = 4, 
                           sharex = True)
    
    plt.subplots_adjust(hspace = 0.0)
    
    

    args = dict(color = "k", lw = 1)
    ax[0].plot(df1.el, **args)
    ax[0].set(ylabel = "Elevação (°)", 
              title = title, 
              ylim = [20, 100], 
              yticks = np.arange(10, 100, 20))

    ax[1].plot(time, stec, **args)
    ax[1].set(ylabel = "STEC (TECU)", 
              ylim = [-40, 10], 
              yticks = np.arange(-30, 10, 10))

    #indexes = find_gaps(df1).gaps
    dtec = df1["stec"] - df1["stec"].rolling("2.5min").mean()
    rot, rot_time, roti, roti_time = rot_and_roti(dtec, time)
   

    ax[2].plot(rot_time, rot, **args)
    ax[2].set(ylabel = "ROT (TECU/min)", 
              ylim = [-12, 12], 
              yticks = np.arange(-10, 12, 5))
    

    ax[3].plot(roti_time, roti, **args)


    delta_lim = datetime.timedelta(hours = 1)
    ax[3].set(ylabel = "ROTI (TECU/min)", 
              ylim = [0, 6], 
              yticks = np.arange(0, 6, 1),
              xlim = [df1.index[0] - delta_lim, 
                      df1.index[-1] + delta_lim], 
              xlabel = "Hora universal (UT)")

    ax[3].xaxis.set_major_formatter(dates.DateFormatter('%H'))
    ax[3].xaxis.set_major_locator(dates.HourLocator(interval = 1))
    
    labels = ["(a)", "(b)", "(c)", "(d)"]
    for num, ax in enumerate(ax.flat):
        
        ax.text(0.9, 0.8, labels[num], transform = ax.transAxes)
    
    
    plt.rcParams.update({'font.size': 12})  
    if save:
        print("Saving...", prn)
        if path_to_save == None:
            path_to_save = "img/roti/{station}/"
        
            
        fig.savefig(f"{path_to_save}Parameters_{station}_{prn}.png", 
                   dpi = 300, 
                   facecolor="white", 
                   transparent=False)
        
        plt.clf()   
        plt.close()
    else:
        plt.show()
        
def main():
    filename = "pbjp.txt"
    prn = "G14"
    station = filename.replace(".txt", "")
    
    df = pd.read_csv(infile + filename, 
             delim_whitespace = True, 
             index_col = "time")
    
    df.index = pd.to_datetime(df.index)
    
    
    path_to_save = "G:\\My Drive\\Doutorado\\Modelos_Latex_INPE\\docs\\Proposal\\Figures\\methods\\"
    
    
    plot_tec_rate(df, 
                  prn, 
                  station, 
                  save = True, 
                  path_to_save = path_to_save)
    
    
main()