from build import build_paths
from ROTI import *
import math
import numpy as np
import os
import pandas as pd
from utils import create_prns


class settings:
    
    LAT_MIN = -60.0
    LAT_MAX = 40.0
    LON_MIN = -120.0
    LON_MAX = -20.0


class MapMaker:
    """
    Construct the matrix based in processed station
    """
    def generate_matrix_tec(list_lat, list_lon, vtec, List_prn, BAD_VALUE):
        """
        Generate a matrix related to the TEC map over a set of lats and longs

        :param list_lat: The list of longitudes from many processed stations
        :param list_lon: The list of latitudes from many processed stations
        :param vtec: The list of vertical TECs, related to the locations (lat, long) from many processed stations
        :return: A matrix in ASCII format, used to build IONEX, PNG, and GTEC
        """
    
        lat_step = int((settings.LAT_MAX - settings.LAT_MIN) / settings.IMAGE_STEP_GRID)
        lon_step = int((settings.LON_MAX - settings.LON_MIN) / settings.IMAGE_STEP_GRID)

        n_sat = len(List_prn)
        counter = np.full([lat_step, lon_step], 0.0)
        matrix = np.full([lat_step, lon_step], 0.0)
        rms = np.full([lat_step, lon_step], 0.0)

        idx_lat = []
        idx_lon = []
            
        for i_prn in range(n_sat):            
            i_lat = math.floor((list_lat[i_prn] - settings.LAT_MIN) / settings.IMAGE_STEP_GRID)
            i_lon = math.floor((list_lon[i_prn] - settings.LON_MIN) / settings.IMAGE_STEP_GRID)

            idx_lat.append(i_lat)
            idx_lon.append(i_lon)

            if not math.isnan(vtec[i_prn]) and 0 <= i_lat < lat_step and 0 <= i_lon < lon_step:

                matrix[i_lat, i_lon] = (matrix[i_lat, i_lon] + vtec[i_prn])
                rms[i_lat, i_lon] = (rms[i_lat, i_lon] + vtec[i_prn]**2)

                counter[i_lat, i_lon] = (counter[i_lat, i_lon] + 1)

        matrix[matrix != 0] = np.divide(matrix[matrix != 0], counter[matrix != 0])
        rms[rms != 0] = np.sqrt(np.divide(rms[rms != 0], counter[rms != 0]))

        matrix[matrix == 0] = BAD_VALUE
        rms[rms == 0] = BAD_VALUE

        return matrix, rms

    @staticmethod
    def full_binning(matrix_raw, BAD_VALUE):
        """
        Not only interpolate, but extrapolate the VTEC of each station, to a more wide and dynamic map

        :param matrix_raw: The ASCII matrix with VTEC above each point location (station)
        :param max_binning: The parameter that specify the limits of extrapolation
        :return: The matrix_raw updated
        """
        max_binning = settings.IMAGE_MAXBINNING
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
    
    
def compute_roti_for_all_stations(year, doy, delta = '2.5min'):
    
    infile = build_paths(year, doy).all_process

    _, _, files = next(os.walk(infile))
    
    result = []
    
    for filename in files:

        df = pd.read_csv(os.path.join(infile, filename), 
                         delim_whitespace = True, 
                         index_col = "time")

        df.index = pd.to_datetime(df.index)
        dt = df.index[0].date()

        df["lon"] = df["lon"] - 360

        

        for prn in create_prns():
            try:
                prn_el = df.loc[(df.prn == prn) & (df.el > 30), :]

                dtec = prn_el["stec"] - prn_el["stec"].rolling(delta).mean()
                time = prn_el.index
                
                rot, rot_tstamps, roti, roti_tstamps = rot_and_roti(dtec, time)
                roti_df = pd.DataFrame({"roti": roti, "prn": prn}, 
                                       index = roti_tstamps)
               
                coords = prn_el.loc[prn_el.index.isin(roti_tstamps), ["lat", "lon"]]
                
                result.append(pd.concat([roti_df, coords], axis = 1))
            except:
                continue

    return pd.concat(result)

def main():
    year = 2022
    doy = 1

    ds = compute_roti_for_all_stations(year, doy)