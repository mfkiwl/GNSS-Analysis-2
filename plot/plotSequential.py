from utils import doy_str_format
from ROTI import *
import matplotlib.dates as dates 
import matplotlib.pyplot as plt
from dcb_calculator import create_prns
from __init__ import *


station = "ceft"
year = 2014
out = []

for doy in range(184, 187): 

    filename  = f"{station}{doy_str_format(doy)}"
    infile = f"Database/all_process/{year}/{station}/{filename}.txt"

    data = pd.read_csv(infile, delim_whitespace = True)

    data.index = pd.to_datetime(data.time)
    
    out.append(data)


df_all = pd.concat(out)

df = out[0]

dt_start = df_all.index[0]
dt_end = df_all.index[-1]


def plotSequential(df, prn, col = "rTEC", save = False):

    fig, ax = plt.subplots(figsize = (10, 10), 
                           nrows = 4, 
                           sharex = True)


    plt.subplots_adjust(hspace = 0)

    df = df.loc[(df.prn == prn) & (df.el > 30), :]

    wargs = dict(color = 'k', lw = 1) ##008AC9

    ax[0].plot(df["el"], **wargs)
    ax[1].plot(df[col], **wargs)

    time = df.index
    stec = df[col].values

    rot, time_rot, roti, time_roti = rot_and_roti(stec, time)

    time_rot = pd.to_datetime(time_rot)
    time_roti = pd.to_datetime(time_roti)

    ax[2].plot(time_rot, rot, **wargs)
    ax[3].plot(time_roti, roti, **wargs)

    ax[3].xaxis.set_major_formatter(dates.DateFormatter('%H:%M'))
    ax[3].xaxis.set_major_locator(dates.HourLocator(interval = 1))


    for num, label in enumerate(["Elevation", col.upper(), 
                                 "ROT", "ROTI"]):
        ax[num].set(ylabel = label)


    ax[3].set(xlabel = "Time (UT)", ylim = [0, 5])
    
    ax[2].set(ylim = [-1, 1])

    date = str(time[0].date())

    fig.suptitle(f"{date}, PRN: {prn}", y = 0.9)

    if save:
        filename  = f"{prn}_{date.replace('-', '')}"
        
        fig.savefig(f'img/ROTI/{filename}.png', 
                    dpi = 100,
                    bbox_inches="tight")

def main():
    
    
    prn = "G06"        #G06, G18, G22
    
    plotSequential(df, prn, col = "stec", save = False)