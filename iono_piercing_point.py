from constants import constants as const
from pyproj import Transformer, CRS
import numpy as np
from load import interpolate_orbits
import pandas as pd
from build import paths
import json

def convert_coords(obs_x, obs_y, obs_z, to_radians = True):
    
    """
    Converts cartezian to geodesic coordinates. 
    Just now, just for the receiver positions.
    The parameters must be in meters [m]
    >>> obs_x, obs_y, obs_z = 5043729.726, -3753105.556, -1072967.067
    >>> print(convert_coords(obs_x, obs_y, obs_z))
    ...-36.6534, -9.7492, 266.23012
    """
    
    crs_from = CRS(proj = 'geocent', ellps = 'WGS84', datum = 'WGS84')
    
    crs_to = CRS(proj = 'latlong', ellps = 'WGS84', datum = 'WGS84')
    
    transformer = Transformer.from_crs(crs_from, crs_to)
    
    lon, lat, alt = transformer.transform(xx = obs_x, 
                                          yy = obs_y, 
                                          zz = obs_z, 
                                          radians = False) 
    
    if to_radians:
        lon = np.radians(lon + 360) 
        lat = np.radians(lat)
    
    return lon, lat, alt




class IonosphericPiercingPoint(object):
    
    def __init__(self, 
                 sat_x, sat_y, sat_z, 
                 obs_x, obs_y, obs_z):
        
        # converts meters to kilometers
        obs_x /= 1000
        obs_y /= 1000
        obs_z /= 1000
        
        # Compute the relative positions
        self.dx = (sat_x - obs_x)
        self.dy = (sat_y - obs_y)
        self.dz = (sat_z - obs_z)

        self.dxdy = (sat_x * obs_y - sat_y * obs_x)
        self.dxdz = (sat_x * obs_z - sat_z * obs_x)
    
    def positions(self, height = "top"):
        
        """Positions of ionospheric piercing point for 
        differents altitudes"""

        if height == "top":
            h = const.alt_top
        else:
            h = const.alt_bottom
            
        arg_1 = pow((self.dy * self.dxdy + self.dz * self.dxdz), 2)
        arg_2 = pow(self.dx, 2) + pow(self.dy, 2) + pow(self.dz, 2)
        arg_3 = pow(self.dxdy, 2) + pow(self.dxdz, 2) - pow(self.dx, 2) * pow(h, 2)
        arg_4 = pow(self.dy, 2) + pow(self.dz, 2) + pow(self.dx, 2)

        factor = np.sqrt(arg_1 - arg_2 * arg_3)

        sub_ion_x = (-1 * (self.dy * self.dxdy + 
                           self.dz * self.dxdz) - factor) / arg_4
        
        sub_ion_y = (self.dy * sub_ion_x + self.dxdy) / self.dx
        sub_ion_z = (self.dz * sub_ion_x + self.dxdz) / self.dx


        return sub_ion_x, sub_ion_y, sub_ion_z
    
    def relative_directions(self, lat, lon):
        
        """
        Relative directions in function of latitude and 
        longitude of receiver (in degrees)
        """
        
        meridional = (-np.cos(lon) * np.sin(lat) * self.dx - 
                      np.sin(lon) * np.sin(lat) * self.dy + 
                      np.cos(lat) * self.dz)

        zonal = - np.sin(lon) * self.dx + np.cos(lon) * self.dy

        vertical = (np.cos(lon) * np.cos(lat) * self.dx + 
                    np.sin(lon) * np.cos(lat) * self.dy + 
                    np.sin(lat) * self.dz)
        
        return meridional, zonal, vertical
    
    def zenital_angle(self, lat, lon):
        
        """Zenital angle between satellite and receiver"""
        
        meridional, zonal, vertical = self.relative_directions(lat, lon)
        
        arg_1 = pow(np.cos(lon) * np.cos(lat), 2)
        arg_2 = pow(np.sin(lon) * np.cos(lat), 2)
        arg_3 = pow(np.sin(lat), 2)
        vertical_norm = np.sqrt(arg_1 + arg_2 + arg_3)
        r = np.sqrt(pow(self.dx, 2) + pow(self.dy, 2) + pow(self.dz, 2))

        return np.arccos(vertical / (r * vertical_norm))
    
    def elevation(self, lat, lon):
        
        """Elevation angle fro zenital angle"""
        
        zangle = self.zenital_angle(lat, lon)
        return ((np.pi / 2.0) - zangle) / const.dtor
    
    def azimuth(self, lat, lon):
        
        """Azimuth angle from relative distances"""
        
        meridional, zonal, vertical = self.relative_directions(lat, lon)
        azimuth_angle = np.arctan2(zonal, meridional)
        if azimuth_angle < 0:
            azimuth_angle += 2.0 * np.pi 
        return azimuth_angle #/ const.dtor
    
    def zenital_iono_angle(self, lat, lon):
        
        """Zenital angle projection in the ionosphere"""
        
        el = self.elevation(lat, lon) * const.dtor
        Re = const.radius_earth
        hm = const.avg_heigth
        return ((np.pi / 2.0) - el - np.arcsin((Re / (Re + hm)) * np.cos(el)))
    
    def ionospheric_sub_point(self, lat, lon):
        
        """ Coordinates of ionospheric piercing point (in degrees)"""
    
        azimuth = self.azimuth(lat, lon)
        zangle_ion = self.zenital_iono_angle(lat, lon)
        
        lat_ip = np.arcsin(np.sin(lat) * np.cos(zangle_ion) + np.cos(lat) * 
                           np.sin(zangle_ion) * np.cos(azimuth))

        lon_ip = lon + np.arcsin((np.sin(zangle_ion) * np.sin(azimuth)) / 
                                 (np.cos(lat_ip)))
    
        return np.degrees(lat_ip), np.degrees(lon_ip)
    
    @property
    def slant_factor(self):
        
        top_ion_x, top_ion_y, top_ion_z = self.positions(height = "top")
        bot_ion_x, bot_ion_y, bot_ion_z = self.positions(height = "bottom")
    
        slant_factor = (pow(top_ion_x - bot_ion_x, 2) + 
                        pow(top_ion_y - bot_ion_y, 2) +
                        pow(top_ion_z - bot_ion_z, 2))
    
        return np.sqrt(slant_factor) / (const.alt_top - const.alt_bottom)



def TEC_projection(elevation):
    """TEC projection """
 
    el = np.radians(elevation)
    Re = const.radius_earth
    hm = const.avg_heigth
    
    return np.cos((Re / (Re + hm)) * np.cos(el))



def piercing_points_data(path,     
                         station, 
                         prn) -> pd.DataFrame:
    
    """Read orbits files fpr each prn and compute the ionospheric 
    Piercing point (given by latitude and longitude)"""
    

    if prn[0] == "R":
        const = "igl"
    elif prn[0] == "G":
        const = "igr"
    
   
    positions = json.load(open(path.fn_json))[station]["position"]
    
    ox, oy, oz = positions[0], positions[1], positions[2]
    
    df = interpolate_orbits(path.fn_orbit(const = const), prn = prn)

    sat_x_vals = df.x.values
    sat_y_vals = df.y.values
    sat_z_vals = df.z.values

    times = df.index
    lon, lat, alt = convert_coords(ox, oy, oz, to_radians = True)
    
    result = { "lon": [], "lat": [], "el": [], "proj": []}
    
    index = []

    for num in range(len(times)):

        sx, sy, sz = sat_x_vals[num], sat_y_vals[num], sat_z_vals[num]
        
        time = times[num]
        
        ip = IonosphericPiercingPoint(sx, sy, sz, ox, oy, oz)

        elevation = ip.elevation(lat, lon)
        
        tec_proj = TEC_projection(elevation)

        lat_ip, lon_ip = ip.ionospheric_sub_point(lat, lon)

        result['lon'].append(lon_ip)
        result['lat'].append(lat_ip)
        result["el"].append(elevation)
        result["proj"].append(tec_proj)
        
        index.append(time)

    return pd.DataFrame(result, index = index)


