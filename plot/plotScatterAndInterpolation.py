from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from tecmap import make_maps
from plotConfig import *
import os
import datetime
from sys import exit

def save(infile = "img/methods/IPP.png"):     
    plt.savefig(infile, dpi = 500, bbox_inches = "tight")
    



    
    
year = 2014
doy = 1
hour = 22
minute = 20
elevation = 10

infile = "Database/roti/2014/001/"

lat_min = -12
lat_max = -2
lon_max = -32
lon_min = -42



_, _, files = next(os.walk(infile))




def filter_data(infile, filename, hour, minute, delta = 10):

    df = pd.read_csv(infile + filename, 
                     delim_whitespace = True)
    
    
    df.index = pd.to_datetime(df.index)
    
    
    dt = df1.index[0].date()
    year, month, day = dt.year, dt.month, dt.day
    
    start = datetime.datetime(year, month, day, hour, minute, 0)
    end = datetime.datetime(year, month, day, hour, minute + (delta - 1), 59)
    
    return df.loc[(df.el > 30) & (df.roti < 5) & 
                  (df.index >= start) & (df.index <= end)]

def run_for_all_stations(files, hour = 0, minute = 0):
   
    out_files = []    
    for filename in files:
        print("processing,", filename)
        out_files.append(filter_data(infile, filename, hour, minute))
        
        
    df = pd.concat(out_files)
    print(df)

exit()

#%%


def plotScatterInterpolation(df, 
                             lon_min = -80, lon_max = -30, 
                             lat_max = 10, lat_min = -40, 
                             step_lon = 10, step_lat = 10, 
                             max_binning = 10):
    
    
    """Plotting piercing points and binning smooth"""

    lats = df.lat.values
    lons = df.lon.values
    values = df.roti.values
    
    p = mapping(width = 15, heigth = 15, ncols = 2)

    fig, ax = p.subplots_with_map()
    
    plt.subplots_adjust(wspace = 0.3)

    matrix, rms = generate_matrix_tec(lats, lons, values, 
                            lat_min = lat_min, 
                            lat_max = lat_max, 
                            lon_min = lon_min, 
                            lon_max = lon_max,
                            step_grid = 0.5, 
                            bad_value = -1)
    
    tecmap = full_binning(matrix, max_binning = max_binning)

    tecmap  = np.where(tecmap == -1, np.nan, tecmap)

    cs = ax[0].scatter(lons, lats, c = values, 
                       cmap = "jet", marker ="o", 
                       s = 15)          
           
            
    x = np.arange(lon_min, lon_max, 0.5)
    y = np.arange(lat_min, lat_max, 0.5)
    levels = np.linspace(0, 5, 100)
    
    img = ax[1].contourf(x, y, tecmap, levels = levels, cmap = "jet")

    def colorbar_setting(img, ax, ticks):
        axins = inset_axes(
                    ax,
                    width="3%",  # width: 5% of parent_bbox width
                    height="100%",  # height: 50%
                    loc="lower left",
                    bbox_to_anchor=(1.05, 0., 1, 1),
                    bbox_transform=ax.transAxes,
                    borderpad=0,
                )
        
        plt.colorbar(img, cax = axins, ticks = ticks)
    
    for ax, img in zip([ax[0], ax[1]], 
                  [cs, img]):
        
        p.mapping_attrs(ax, step_lat = 10, 
                            step_lon = 10,
                            lat_min = -40.0, 
                            lat_max = 10.0, 
                            lon_min = -80.0, 
                            lon_max = -30.0)
        
        colorbar_setting(img, ax, 
                         ticks = [0, 1, 2, 3, 4, 5])

        p.equator(ax)
    date = df.index[0].strftime("%d/%m/%Y %H:00 UT")
        
    fig.suptitle(date, y = 0.7)
    
    
    #save()
    plt.show()
    
plotScatterInterpolation(df)