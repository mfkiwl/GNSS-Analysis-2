from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from tecmap import  generate_matrix_tec, full_binning
from plot.plotConfig import *
from plot.plotMagneticEquator import plot_equator
import os
import datetime


year = 2014
doy = 1


infile = "Database/roti/2014/001/"

_, _, files = next(os.walk(infile))

def load_and_filter(infile, filename, hour, 
                    minute, delta = 10, elevation = 30):

    df = pd.read_csv(infile + filename, delim_whitespace = True)

    df.index = pd.to_datetime(df.index)

    dt = df.index[0].date()

    year, month, day = dt.year, dt.month, dt.day

    start = datetime.datetime(year, month, day, hour, minute, 0)

    end = datetime.datetime(year, month, day, hour, minute + (delta - 1), 59)    
    
    return df.loc[(df.index >= start) & (df.index < end) & (df.el > elevation), :]


def run_for_all_files(files, hour, minute, elevation = 30):
    out = []
    for filename in files:
        try:
            out.append(load_and_filter(infile, 
                                       filename, 
                                       hour, minute, 
                                       elevation = elevation))
        except:
            print(filename)
            continue
            
    return pd.concat(out)


hour = 22
minute = 20
elevation = 20

df = run_for_all_files(files, hour, minute, elevation = elevation)

lat_min = -12
lat_max = -2
lon_max = -32
lon_min = -42


def plot_scatter(df, lon_min = -80, lon_max = -30, 
                 lat_max = 10, lat_min = -40, 
                 step_lon = 10, step_lat = 10, max_binning = 10):

    df1 = df.loc[(lat_min < df.lat) & 
                 (df.lat < lat_max) & 
                 (lon_min < df.lon) &
                 (df.lon < lon_max), :]
    
    lats = df1.lat.values
    lons = df1.lon.values
    values = df1.roti.values
    
    
    
    p = plotting()

    fig, ax = p.subplots_with_map(width = 15, heigth = 15, ncols = 2)
    
    plt.subplots_adjust(wspace = 0.5)

    matrix, rms = generate_matrix_tec(lats, lons, values, 
                            lat_min = lat_min, 
                            lat_max = lat_max, 
                            lon_min = lon_min, 
                            lon_max = lon_max,
                            step_grid = 0.5, bad_value = -1)
    
    tecmap = full_binning(rms, max_binning = max_binning)

    tecmap  = np.where(tecmap == -1, np.nan, tecmap)
    #tecmap  = np.where(tecmap > 5, 5, tecmap)

    for num, ax in enumerate(ax.flat):
        
        
        
        if num == 0:
            img = ax.scatter(lons, lats, c = values, cmap = "jet", 
                             vmin = 0, vmax = None, marker ="s")          
        else:       
            
            x = np.arange(lon_min, lon_max, 0.5)
            y = np.arange(lat_min, lat_max, 0.5)
            levels = np.linspace(0, 2.5, 50)
            
            img = ax.contourf(x, y, tecmap, levels = levels, cmap = "jet")
    
        p.setting_states_map(ax, 
                             step_lat = step_lat, 
                             step_lon = step_lon,
                             lat_min = lat_min, 
                             lat_max = lat_max, 
                             lon_max = lon_max, 
                             lon_min = lon_min)
                
        axins = inset_axes(
                            ax,
                            width="3%",  # width: 5% of parent_bbox width
                            height="100%",  # height: 50%
                            loc="lower left",
                            bbox_to_anchor=(1.05, 0., 1, 1),
                            bbox_transform=ax.transAxes,
                            borderpad=0,
                        )

        plt.colorbar(img, cax = axins) #ticks = [0, 1, 2, 3, 4, 5])
        #equator(ax)
    date = df.index[0].strftime("%Y-%m-%d %H:%M")
        
    fig.suptitle(date, y = 0.7)
    
    def save(infile = "img/methods/IPP.png"):     
      
        plt.savefig(infile, dpi = 500, bbox_inches = "tight")
    #save()
    plt.show()
    
plot_scatter(df,
             lat_min = -12, 
             lat_max = -2, 
             lon_max = -32, 
             lon_min = -42, 
             step_lon = 1, 
             step_lat= 1, 
             max_binning = 3
             )


def equator(ax):
    eq = pd.read_csv("Database/geo/Inclination2021.txt", 
                     delim_whitespace = True)
    
    eq = pd.pivot_table(eq, columns = "lon", index = "lat", values = "B")
    
    cs = ax.contour(eq.columns, eq.index, eq.values, 1, 
               linewidths = 3, colors = "red", 
                transform = ccrs.PlateCarree())
    
    cs.cmap.set_over('red')
