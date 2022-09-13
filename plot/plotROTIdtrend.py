from build import build_paths
import matplotlib.pyplot as plt
import pandas as pd
import matplolib.dates as dates
from ROTI import rot_and_roti


station = "mgbh"
year = 2015
doy = 131
 

infile = build_paths(year, doy).all_process

df = pd.read_csv(infile, delim_whitespace = True, index_col = "time")

save = True
prn = "G02"
df = df.loc[(df.prn == prn) & (df.el > 30), :]

df.index = pd.to_datetime(df.index)


fig, ax = plt.subplots(figsize = (10, 6), 
                       nrows = 2, ncols = 2, 
                       sharex = True)


plt.subplots_adjust(hspace = 0)
time = df.index
stec = df.stec.values

rot, rot_tstamps, roti, roti_tstamps = rot_and_roti(stec, time)
ax[0, 0].plot(rot_tstamps, rot)
ax[1, 0].plot(roti_tstamps, roti)

ax[0, 0].set(ylabel = "ROT", title = "Dados brutos", ylim = [-5, 5])
ax[0, 1].set(ylabel = "ROT", title = "dTrend (2.5 min)", ylim = [-5, 5])


dtec = df["stec"] - df["stec"].rolling('2.5min').mean()

rot, rot_tstamps, roti, roti_tstamps = rot_and_roti(dtec, time)
ax[0, 1].plot(rot_tstamps, rot)
ax[1, 1].plot(roti_tstamps, roti)


ax[1, 1].set(ylabel = "ROTI",  ylim = [0, 3], xlabel = "Tempo (UT)")
ax[1, 0].set(ylabel = "ROTI",  ylim = [0, 3], xlabel = "Tempo (UT)")

ax[1, 1].axhline(max(roti), color = "k", linestyle = "--")
ax[1, 0].axhline(max(roti), color = "k", linestyle = "--")


for ax in ax.flatten():
    ax.axhline(0, color = "k", linestyle = "--")
    ax.xaxis.set_major_formatter(dates.DateFormatter('%H:%M'))
    ax.xaxis.set_major_locator(dates.HourLocator(interval = 1))

date = df.index[0].date()

fig.suptitle(f"{station} - {prn} - {date}")

if save:
    filename  = f"{prn}_{str(date).replace('-', '')}"
    
    fig.savefig(f'img/ROTI/{filename}.png', 
                dpi = 100,
                bbox_inches="tight")
plt.show()