import os
import pandas as pd
import numpy as np
from build import paths
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import cartopy.feature as cf
import cartopy.crs as ccrs
import datetime
from utils import doy_str_format
from terminator import *
from __init__ import *
from tecmap import MapMaker
from scipy import interpolate


def generate_matrix_tec(lat_list, lon_list, roti_list, 
               lat_min = -60, lat_max = 40, 
               lon_min = -120, lon_max = -20, 
               step_grid = 0.5, bad_value = -1):
    
    tec = roti_list.copy()
    
    lat_step = int((lat_max - lat_min) / step_grid)
    lon_step = int((lon_max - lon_min) / step_grid)

    counter = np.zeros((lat_step, lon_step))
    matrix = np.zeros((lat_step, lon_step))
    rms = np.zeros((lat_step, lon_step))

    idx_lat = []
    idx_lon = []
    for num in range(len(lat_list)):            

        # A função do numpy retorna floats (104.0) enquanto o math retorna integers (104)
        i_lat = np.floor((lat_list[num] - lat_min) / step_grid).astype(int)
        i_lon = np.floor((lon_list[num] - lon_min) / step_grid).astype(int)

        idx_lat.append(i_lat)
        idx_lon.append(i_lon)

        if (0 <= i_lat < lat_step) and (0 <= i_lon < lon_step):

            matrix[i_lat, i_lon] = (matrix[i_lat, i_lon] + tec[num])
            rms[i_lat, i_lon] = (rms[i_lat, i_lon] + tec[num]**2)
            counter[i_lat, i_lon] = (counter[i_lat, i_lon] + 1)
           

    matrix[matrix != 0] = np.divide(matrix[matrix != 0], counter[matrix != 0])
    rms[rms != 0] = np.sqrt(np.divide(rms[rms != 0], counter[rms != 0]))
    
    # testar diferentes condições para essa substituição
    matrix[matrix == 0] = bad_value
    rms[rms == 0] = bad_value
    
    return matrix, rms 


def full_binning(matrix_raw, BAD_VALUE = -1, max_binning = 10):

    
    n_lon = matrix_raw.shape[1]
    n_lat = matrix_raw.shape[0]
    result_matrix = np.full([n_lat, n_lon], BAD_VALUE)

    current_matrix = matrix_raw

    if max_binning > 0:
        for n_binning in range(1, max_binning + 1):
            for i_lat in range(n_binning, (n_lat - n_binning - 1)):
                for i_lon in range(n_binning, (n_lon - n_binning - 1)):

                    sub_mat_raw = matrix_raw[(i_lat - n_binning):(i_lat + n_binning),
                                (i_lon - n_binning):(i_lon + n_binning)]
                    
                    total_valid_tec_raw = (sub_mat_raw != BAD_VALUE).sum()

                    if (total_valid_tec_raw > 0) & (result_matrix[i_lat, i_lon] == BAD_VALUE):
                        sub_mat = current_matrix[(i_lat - n_binning):(i_lat + n_binning),
                                 (i_lon - n_binning):(i_lon + n_binning)]
                        
                        
                        total_sub_mat = sub_mat[sub_mat != BAD_VALUE].sum()
                        total_valid_tec = (sub_mat != BAD_VALUE).sum()
                        
                        
                        tec_medio = BAD_VALUE

                        if total_valid_tec > 0:
                            tec_medio = total_sub_mat / total_valid_tec
                            
                        result_matrix[i_lat, i_lon] = tec_medio
                        
            current_matrix = result_matrix
    else:
        result_matrix = matrix_raw

    return result_matrix

def make_maps(ds, hour, minute, delta = 10, 
              lat_min = -30.0, lat_max = 10.0, 
              lon_min = -70.0, lon_max = -10.0):
    """Separe the data in specifics time range for construct the TEC MAP"""

    dt = ds.index[0].date()

    year, month, day = dt.year, dt.month, dt.day

    start = datetime.datetime(year, month, day, hour, minute, 0)
    end = datetime.datetime(year, month, day, hour, minute + (delta - 1), 59)

    res = ds.loc[(ds.index >= start) & (ds.index <= end)]

    lat_list = res.lat.values
    lon_list = res.lon.values
    roti_list = res.roti.values

    tec_matrix, rms_tec = generate_matrix_tec(lat_list, lon_list, roti_list, 
                                              lat_min = lat_min, lat_max = lat_max, 
                                              lon_min = lon_min, lon_max = lon_max)
    
    return full_binning(tec_matrix, -1, max_binning = 10)

def maps_and_times(infile, 
                   morning = 7, 
                   evening = 21, 
                   delta = 10, 
                   lat_min = -30.0, lat_max = 10.0, 
                   lon_min = -70.0, lon_max = -10.0):
    
    df = pd.read_csv(infile, delim_whitespace = True)
    
    df.index = pd.to_datetime(df.index)
    dt = df.index[0].date()
    
    year, month, day = dt.year, dt.month, dt.day
    
    times = []
    roti_maps = []
    for hour in range(0, 24):
        for minute in range(0, 60, delta):
            if (hour > evening) or (hour < morning):
                
                times.append(datetime.datetime(year, month, day, 
                                               hour, minute, 0))
               
                
                roti_maps.append(make_maps(df, hour, minute, delta = delta, 
                                           lat_min = lat_min, lat_max = lat_max, 
                                           lon_min = lon_min, lon_max = lon_max))
            
    return times, roti_maps
        
      
        

def setting_states_map(ax, step_lat = 10, step_lon = 10,
                       lat_min = -30.0, lat_max = 10.0, 
                       lon_min = -70.0, lon_max = -10.0):    
    
    
    ax.set_global()

    ax.gridlines(color = 'grey', linestyle = '--', 
             crs=ccrs.PlateCarree())

    states_provinces = cf.NaturalEarthFeature(
                    category='cultural',
                    name='admin_1_states_provinces_lines',
                    scale='50m',
                    facecolor='none')


    ax.add_feature(states_provinces, edgecolor='black')
    ax.add_feature(cf.COASTLINE, edgecolor='black', lw = 2) 
    ax.add_feature(cf.BORDERS, linestyle='-', edgecolor='black')

    ax.set(ylabel = 'Latitude (°)', xlabel = 'Longitude (°)')
    

    ax.set_extent([lon_min, lon_max, lat_min, lat_max], 
                  crs=ccrs.PlateCarree())

    ax.set_xticks(np.arange(lon_min, lon_max + step_lat, step_lon), 
                              crs=ccrs.PlateCarree()) 

    ax.set_yticks(np.arange(lat_min, lat_max + step_lat, step_lat), 
                  crs=ccrs.PlateCarree())
    



def plotROTImaps(i, save = True):
    
    
    if save:
        plt.ioff()
        
        
    fig = plt.figure(figsize = (8, 8))
    ax = plt.axes(projection = ccrs.PlateCarree())
    
    tecmap = roti_maps[i]
    date = times[i]
    
    levels = np.linspace(0, 5, 50)
    tecmap = np.where(tecmap < 0, np.nan, tecmap)
    
    
    yy = np.linspace(-60.0, 40.0, tecmap.shape[1])
    xx = np.linspace(-120.0, -20.0, tecmap.shape[0])

    yy = np.arange(-30.0, 10.0, 0.5)
    xx = np.arange(-70.0, -10.0, 0.5)
    
    #print(len(yy), len(xx))
    img = ax.contourf(xx, yy, tecmap, levels = levels, cmap = "jet")
    #lon, lat = np.meshgrid(xx, yy)
    #levels = 50
    #img = ax.contourf(lon, lat, tecmap, levels = levels, cmap = "jet")

    cbar_ax = fig.add_axes([0.95, 0.12, 0.03, 0.75]) #xposition, yposition, espessura, altura

    cb = plt.colorbar(img, cax=cbar_ax)
                      #ticks= [0, 1, 2, 3, 4, 5])

    cb.set_label(r'ROTI (TECU/min)')

    setting_states_map(ax)

    ax.set(title = date)

    a_lon_term, a_lat_term = terminator(date, 18)
    
    x = np.array(a_lon_term) 
    y = np.array(a_lat_term)
    f = interpolate.interp1d(x, y, fill_value="extrapolate")
    
    xnew = np.arange(-180, 180, 1)
    ynew = f(xnew)
    ax.plot(xnew, ynew,  "--", color = "k", lw = 3)
 
    da = pd.read_csv("mag_inclination_2021.txt", 
                     delim_whitespace = True)

    da = pd.pivot_table(da, values = "B", 
                        index = "lat", columns = "lon")

    ax.contour(da.columns, da.index, da.values, 1, 
               linewidths = 2, color = 'k',
                transform = ccrs.PlateCarree())
    
    if save:
        filename = str(date).replace("-", "").replace(" ", "").replace(":", "")
        plt.savefig(f'img/maps/{filename}.png', 
                    dpi = 80, bbox_inches="tight")
    else:
        plt.show()

year = 2014
doy = 1
infile = f"Database/roti/{year}/{doy_str_format(doy)}.txt"
times, roti_maps = maps_and_times(infile, morning = 7, evening = 20, delta = 5) 

"""
for i, time in enumerate(times):
    
    print(i, time)
    plotROTImaps(i, save = True)
    



print(roti_maps[110].max())

"""
#pd.DataFrame(roti_maps[1]).to_excel("test_roti.x")

plotROTImaps(110, save = False)


tecmap = roti_maps[110]
xsize, ysize = tecmap.shape
print(xsize, ysize)
tecmap = np.where(tecmap < 0, np.nan, tecmap)

