import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import os 
import cartopy.crs as ccrs
import matplotlib.dates as dates
from plot.plotTECmaps import plotTECmap
import cv2

def load_and_plot_roti(ax, rotiInfile, start_date, end_date, delta = 2):


    df = pd.read_csv(rotiInfile, 
                     delim_whitespace = True, 
                     index_col = 0)

    df.index = pd.to_datetime(df.index)
    
    
    df2 = df.loc[(df.delta == delta) & 
                 (df.index >= start_date) & 
                 (df.index <= end_date), :]

    col = "total"
    ax.plot(df2[col], color = "k")
    
    year, month, day = start_date.year, start_date.month, start_date.day 
    
    
    ax.xaxis.set_major_formatter(dates.DateFormatter('%H:%M'))
    ax.xaxis.set_major_locator(dates.HourLocator(interval = 1))
    
    #start_del = datetime.datetime(year, month, day, 22, n)
    #end_del = datetime.datetime(year, month, day, 22, n + delta)
    #ax.axvspan(start_del, end_del, alpha=0.2, color = "gray")
    
def plot_image(infile, filename, ax):

    img = cv2.imread(infile + filename)
    
    ax.imshow(img, aspect = "auto")
    ax.set(xticks = [], yticks = [])

plt.figure(figsize=(18, 9))
G = gridspec.GridSpec(3, 3)

ax1 = plt.subplot(G[0, :])


rotiInfile = "results/database/max_rotis/"

_,_, roti_files = next(os.walk(rotiInfile))
    
rotiFilename = roti_files[0]

rotiInfile = rotiInfile + rotiFilename

year, month = 2014, 1

day = 1

start_date = datetime.datetime(year, month, day, 21, 0)
end_date = datetime.datetime(year, month, day + 1, 7, 0)

load_and_plot_roti(ax1, rotiInfile, start_date, end_date, delta = 2)



ax2 = plt.subplot(G[1:, -1],  projection = ccrs.PlateCarree())


tecInfile = "C:\\TEC_2014\\TEC_2014_01\\"


_, _, tec_files = next(os.walk(tecInfile))

tecFilename = tec_files[0]

plotTECmap(ax2, tecInfile, tecFilename)

ax3 = plt.subplot(G[1:, 0])

ionoInfile = "G:\\My Drive\\Python\\data-analysis\\digisonde\\img\\2014_test\\"

_, _, iono_files = next(os.walk(ionoInfile))

ionoFilename = iono_files[0]

plot_image(ionoInfile, ionoFilename,  ax3)

ax4 = plt.subplot(G[1:, -2])


imagerInfile = "G:/My Drive/Python/data-analysis/imager/database/2014/001_test/"

_, _, imager_files = next(os.walk(imagerInfile))

imagerFilename = imager_files[0]

plot_image(imagerInfile, imagerFilename, ax4)

plt.tight_layout()
plt.show()