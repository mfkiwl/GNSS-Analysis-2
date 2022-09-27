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

def load_and_plot_roti(ax, rotiInfile, 
                       start_date, end_date, 
                       delta = 2):


    df = pd.read_csv(rotiInfile, 
                     delim_whitespace = True, 
                     index_col = 0)

    df.index = pd.to_datetime(df.index)
    
    
    df2 = df.loc[(df.delta == delta) & 
                 (df.index >= start_date) & 
                 (df.index <= end_date), :]

    col = "total"
    ax.plot(df2[col], color = "k", lw = 2)
    
    year, month, day = start_date.year, start_date.month, start_date.day 
    
    
    ax.xaxis.set_major_formatter(dates.DateFormatter('%H:%M'))
    ax.xaxis.set_major_locator(dates.HourLocator(interval = 1))
    
    return df2
 
def shade(ax, start, end):
    ax.axvspan(start, end, alpha=0.2, color = "gray")
    
def plot_image(infile, filename, ax):

    img = cv2.imread(infile + filename)
    
    ax.imshow(img, aspect = "auto")
    ax.set(xticks = [], yticks = [])
    
    
def get_files(infile): 
    _, _, files = next(os.walk(infile))
    return files

def imager_fname(filename):
    """Convert filename attributes into datetime format"""
    if ".tif" in filename:
        infos = filename.replace(".tif", "").split("_")
    else:
        infos = filename.replace(".png", "").split("_")

    date = infos[2]
    time = infos[-1]
    return datetime.datetime.strptime(date + " " + time, '%Y%m%d %H%M%S')

def ionosonde_fname(filename):
    """Convert digisonde filename (EMBRACE format) to datetime"""
    args = filename.split("_")
    code = args[0]
    date = args[1][:8]
    time = args[1][13:-4]
    return datetime.datetime.strptime(date + time, "%Y%m%d%H%M%S")


def tec_fname(filename):
    """Convert TEC filename (EMBRACE format) to datetime"""
    args = filename.split('_')
    date = args[1][:4] + '-' + args[1][4:6]+ '-' +args[1][-2:] 
    time = args[-1].replace('.txt', '')
    time = time[:2] + ':' + time[2:]
    
    return datetime.datetime.strptime(date + ' ' + time, "%Y-%m-%d %H:%M")










year, month = 2014, 1

day = 1



rotiInfile = "G:\\My Drive\\Python\\data-analysis\\results\\database\\max_rotis\\"
tecInfile = "C:\\TEC_2014\\TEC_2014_01\\"
ionoInfile = "G:\\My Drive\\Python\\data-analysis\\digisonde\\img\\2014_test\\"
imagerInfile = "G:/My Drive/Python/data-analysis/imager/database/2014/001_test/"

tec_files = get_files(tecInfile)
tecFilename = tec_files[0]

iono_files = get_files(ionoInfile)
ionoFilename = iono_files[0]

imager_files =  get_files(imagerInfile)
imagerFilename = imager_files[0]


roti_files = get_files(rotiInfile)
rotiFilename = roti_files[0]


def plot_quadri_observation(imagerInfile, 
                            ionoInfile, 
                            tecInfile, 
                            imagerFilename, 
                            ionoFilename, 
                            tecFilename, save = False):
    
    if save:
        plt.ioff()
        
        
    fig = plt.figure(figsize = (18, 9))
    
    plt.subplots_adjust(wspace = 0.2, hspace = 0.5)
    G = gridspec.GridSpec(3, 3)
    
    ax1 = plt.subplot(G[0, :])
    
    start_date = datetime.datetime(year, month, day, 21, 0)
    end_date = datetime.datetime(year, month, day + 1, 7, 0)
    
    df = load_and_plot_roti(ax1, rotiInfile + rotiFilename, start_date, 
                            end_date, delta = 2)
    
    
    ax2 = plt.subplot(G[1:, -1],  projection = ccrs.PlateCarree())
    
    
    plotTECmap(ax2, tecInfile, tecFilename)
    
    
    shade(ax1,
          datetime.datetime(2014, 1, 1, 22, 0), 
          datetime.datetime(2014, 1, 1, 22, 10))
    
    ax3 = plt.subplot(G[1:, 0])
    
    
    
    plot_image(ionoInfile, ionoFilename, ax3)
    
    ax4 = plt.subplot(G[1:, -2])
    
    
    
    plot_image(imagerInfile, imagerFilename, ax4)
    
    if save:
        filename = imager_fname(imagerFilename)
        print("Saving...", filename)
        name_to_save = filename.strftime("%Y%m%d%H%M%S")
        fig.savefig(f"C:\\tri_observation\\{name_to_save}.png", 
                   dpi = 80, bbox_inches="tight")
    else:
        plt.show()