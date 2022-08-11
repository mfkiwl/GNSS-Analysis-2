# -*- coding: utf-8 -*-
"""
Created on Wed Aug 10 15:29:00 2022

@author: Luiz
"""

import datetime
import numpy as np
import pandas as pd
from pyproj import Transformer, CRS
from load import load_orbits, load_receiver


def sub_ion_point(altiono, 
                  sat_x, sat_y, sat_z, 
                  obs_x, obs_y, obs_z):
    
    """sub-Ionospheric point"""
    
    alpha = sat_y - obs_y
    phi = sat_x * obs_y - sat_y * obs_x
    beta = sat_z - obs_z
    theta = sat_x * obs_z - sat_z * obs_x
    gamma = sat_x - obs_x

    arg_1 = np.power((alpha * phi + beta * theta), 2.0)
    
    arg_2 = (np.power(alpha, 2.0) + 
             np.power(beta, 2.0) + 
             np.power(gamma, 2.0))
    
    arg_3 = (np.power(phi, 2.0) + 
             np.power(theta, 2.0) - 
             np.power(gamma, 2.0) * 
             np.power(altiono, 2.0))
    
    fator = np.sqrt(arg_1 - arg_2 * arg_3)

    arg_4 = (np.power(alpha, 2.0) + np.power(beta, 2.0) + np.power(gamma, 2.0))
    
    
    dum = (-1 * (alpha * phi + beta * theta) - fator) / arg_4

    aux_dum = (sat_x - dum) * (obs_x - dum)

    for i, item in enumerate(aux_dum):
        if item > 0:
            dum[i] = (-1 * (alpha[i] * phi[i] + beta[i] * 
                            theta[i]) + fator[i]) / (
                            np.power(alpha[i], 2.0) + 
                            np.power(beta[i], 2.0) + 
                            np.power(gamma[i], 2.0))

    sub_ion_x = dum
    sub_ion_y = (alpha * dum + phi) / gamma
    sub_ion_z = (beta * dum + theta) / gamma

    return sub_ion_x, sub_ion_y, sub_ion_z


def directions(sat_x, sat_y, sat_z, 
               obs_x, obs_y, obs_z, 
               long_obs, lat_obs):
    
    
    dx = (sat_x - obs_x)
    dy = (sat_y - obs_y)
    dz = (sat_z - obs_z)

    north = (-np.cos(long_obs) * np.sin(lat_obs) * dx - 
              np.sin(long_obs) * np.sin(lat_obs) * dy + 
              np.cos(lat_obs) * dz)
    
    east = - np.sin(long_obs) * dx + np.cos(long_obs) * dy

    vertical = (np.cos(long_obs) * np.cos(lat_obs) * dx + 
                np.sin(long_obs) * np.cos(lat_obs) * dy + 
                np.sin(lat_obs) * dz)

    return north, east, vertical


def vertical_angle(sat_x, sat_y, sat_z, 
                   obs_x, obs_y, obs_z, 
                   long_obs, lat_obs, vertical):
    
    
    v1 = np.power(np.cos(long_obs) * np.cos(lat_obs), 2.0)
    v2 = np.power(np.sin(long_obs) * np.cos(lat_obs), 2.0)
    v3 = np.power(np.sin(lat_obs), 2.0)
    
    vertical_norm = np.sqrt(v1 + v2 + v3)
    
    r = np.sqrt(np.power(sat_x - obs_x, 2.0) + 
               np.power(sat_y - obs_y, 2.0) + 
               np.power(sat_z - obs_z, 2.0))

    return np.arccos(vertical / (r * vertical_norm))

def elevation_and_azimuth(zangl, dtor, east, north):
    elevation = ((np.pi / 2.0) - zangl) / dtor
    azimuth = np.arctan2(east, north)
    azimuth[azimuth < 0] += 2.0 * np.pi
    azimuth = azimuth / dtor
    return elevation, azimuth


def zangle_in_ionosphere(elevation, dtor, 
                         radius_earth, avg_heigth):

    return ((np.pi / 2.0) - (elevation * dtor) - 
            np.arcsin((radius_earth / (radius_earth + avg_heigth)) * 
                      np.cos(elevation * dtor)))



def piercing_point_coords(lat_obs, long_obs, w, 
                          azimuth, dtor):

    Latpp = np.arcsin(np.sin(lat_obs) * np.cos(w) + 
                  np.cos(lat_obs) * np.sin(w) * 
                  np.cos(azimuth * dtor))

    Lonpp = (long_obs + np.arcsin((np.sin(w) * 
                               np.sin(azimuth * dtor)) / 
                              (np.cos(Latpp))))
    
    
    return np.rad2deg(Latpp[0]), np.rad2deg(Lonpp[0])


def TEC_projection(radius_earth, avg_heigth, elevation):
   
   
    zen_comma = np.arcsin((radius_earth / 
                       (radius_earth + avg_heigth)) * 
                        np.cos(np.deg2rad(elevation)))

    return np.cos(zen_comma)
   
def slant_factor(top_ion_x, bot_ion_x, 
                 top_ion_y, bot_ion_y, 
                 top_ion_z, bot_ion_z, 
                 alt_bottom, alt_top):
 
    slant_factor = (np.power(top_ion_x - bot_ion_x, 2.0) + 
                    np.power(top_ion_y - bot_ion_y, 2.0) +
                    np.power(top_ion_z - bot_ion_z, 2.0))
 
    return (np.sqrt(slant_factor) / (alt_top - alt_bottom))
     
def convert_coords(obs_x, obs_y, obs_z):
    
    crs_from = CRS(proj='geocent', 
                   ellps='WGS84', 
                   datum='WGS84')
    crs_to = CRS(proj='latlong', 
                 ellps='WGS84', 
                 datum='WGS84')
    
    transformer = Transformer.from_crs(crs_from, 
                                       crs_to)
    
    lon, lat, alt = transformer.transform(xx=obs_x, 
                                          yy=obs_y, 
                                          zz=obs_z, 
                                          radians = False) 
    return lon, lat, alt




def main(obs_x, obs_y, obs_z, 
         sat_x_vals, sat_y_vals, sat_z_vals):

    # Altitudes da ionosfera
    alt_bottom = 6620.0
    alt_top = 6870.0
    
    radius_earth = 6371.0  # re
    avg_heigth = 250.0  # hm
    
    rad2deg = 57.2958
    dtor = 0.0174533
    
    
    
    lon, lat, alt = convert_coords(obs_x, obs_y, obs_z)
    deg2rad = np.pi / 180.0
    long_obs = (lon + 360) * deg2rad
    lat_obs = lat * deg2rad
    
    obs_x /= 1000
    obs_y /= 1000
    obs_z /= 1000
    
    result = []
    
    for sat_x, sat_y, sat_z in zip(sat_x_vals, sat_y_vals, sat_z_vals):
        
        top_ion_x, top_ion_y, top_ion_z = sub_ion_point(alt_top, 
                                                        sat_x, sat_y, sat_z, 
                                                        obs_x, obs_y, obs_z)
        bot_ion_x, bot_ion_y, bot_ion_z = sub_ion_point(alt_bottom, 
                                                        sat_x, sat_y, sat_z, 
                                                        obs_x, obs_y, obs_z)
        
        '''
         slant_factor_ = slant_factor(top_ion_x, bot_ion_x, 
                                     top_ion_y, bot_ion_y, 
                                     top_ion_z, bot_ion_z, 
                                     alt_bottom, alt_top)
        
         
        
        '''
        
        north, east, vertical = directions(sat_x, sat_y, sat_z, 
                                           obs_x, obs_y, obs_z, 
                                           long_obs, lat_obs)
        
        
        
        
        zangl = vertical_angle(sat_x, sat_y, sat_z, 
                           obs_x, obs_y, obs_z, 
                           long_obs, lat_obs, vertical)
        
        elevation, azimuth = elevation_and_azimuth(zangl, dtor, east, north)
    
        if elevation > 0:
        
            w = zangle_in_ionosphere(elevation, dtor, 
                                     radius_earth, avg_heigth)
            
            Latpp, Lonpp = piercing_point_coords(lat_obs, long_obs, 
                                                 w, azimuth, dtor)
        
            result.append([Latpp, Lonpp])
        
    return np.array(result)
 
    






