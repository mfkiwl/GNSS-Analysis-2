import pandas as pd
from plotConfig import mapping
from plot.plotMappingRange import *
from build import paths, tex_path

p = mapping(width = 20, heigth = 20, ncols = 1 )


fig, ax = p.subplots_with_map()

p.mapping_attrs(ax, 
                step_lat = 2, step_lon = 2,
                lat_min = -12, lat_max = -2, 
                lon_max = -32, lon_min = -42)



plotStations(ax, 
            date = datetime.date(2014, 1, 1), 
            color = "green", 
            markersize = 15, 
            marker = "o",   
            lat_min = -12, 
            lat_max = -2, 
            lon_max = -32, 
            lon_min = -42)


plot_range_stations(ax)


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

leg = plt.legend([l1, l2, l3], labels, 
                 fontsize = 30,
                 loc = "upper right", 
                 )

filename = "northeast_region.png"
fig.savefig(os.path.join(tex_path("results"), filename),
            dpi = 500
            )