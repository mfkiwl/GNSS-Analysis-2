import os
import plotConfig as p
import datetime
import plot.plotMappingRange as ran
from build import paths, tex_path
import matplotlib.pyplot as plt


def plotNortheastInstrumentation():
    map = p.mapping(width = 20, heigth = 20, ncols = 1 )
    
    
    fig, ax = map.subplots_with_map()
    
    map.mapping_attrs(ax, 
                    step_lat = 2, step_lon = 2,
                    lat_min = -12, lat_max = -2, 
                    lon_max = -32, lon_min = -42)
    
    
    
    ran.plotStations(ax, 
                date = datetime.date(2014, 1, 1), 
                color = "green", 
                markersize = 15, 
                marker = "o",   
                lat_min = -12, 
                lat_max = -2, 
                lon_max = -32, 
                lon_min = -42)
    
    
    ran.plot_range_stations(ax)
    
    
    size = 300
    
    l1 = plt.scatter([],[], s = size, 
                     color = 'green', 
                     marker = "o",
                     edgecolors='none')
    
    
    l2 = plt.scatter([],[], s = size, 
                     color = 'red', 
                     marker = 's', 
                     edgecolors='none')
    
    
    l3 = plt.scatter([],[], s = size, 
                     color = 'blue', 
                     marker = '^', 
                     edgecolors='none')
    
    labels = ["Receptores GNSS - RBMC", 
              "Imageador (Cariri)", 
              "Ionossonda (Fortaleza)"]
    
    plt.legend([l1, l2, l3], labels, 
                     fontsize = 30,
                     loc = "upper right", 
                     )
    
    return fig

def main():

    fig = plotNortheastInstrumentation()
    
    path_to_save = os.path.join(tex_path("results"), 
                                "northeast_region.png")
    
    
    fig.savefig(path_to_save, dpi = 100)
    
    
    