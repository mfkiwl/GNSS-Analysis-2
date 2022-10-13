import datetime 
import numpy as np
import pandas as pd

lat_min = -30.0 
lat_max = 10.0 
lon_min = -70.0 
lon_max = -10.0


def generate_matrix_tec(lat_list, lon_list, roti_list, 
                        lat_min, lat_max, 
                        lon_min, lon_max, step_grid = 0.5, bad_value = -1):
    
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

class make_maps:
    
    """Separe the data in specifics time range for construct the TEC MAP"""
    
    def __init__(self, df, hour, minute, delta = 10):
    
        dt = df.index[0].date()
        year, month, day = dt.year, dt.month, dt.day
    
        self.start = datetime.datetime(year, month, day, hour, minute, 0)
        self.end = datetime.datetime(year, month, day, hour, minute + (delta - 1), 59)
    
        self.res = df.loc[(df.index >= self.start) & (df.index <= self.end)]
    
        self.lat = self.res.lat.values
        self.lon = self.res.lon.values
        self.roti = self.res.roti.values
    
    def matrix(self, 
               lat_min = -30.0, lat_max = 10.0, 
               lon_min = -70.0, lon_max = -10.0):
        """Returns tec and rms matrizes"""
        
        self.lat_min = lat_min
        self.lat_max = lat_max
        self.lon_min = lon_min
        self.lon_max = lon_max
    
        return generate_matrix_tec(self.lat, self.lon, self.roti, 
                                   lat_min = self.lat_min, 
                                   lat_max = self.lat_max, 
                                   lon_min = self.lon_min, 
                                   lon_max = self.lon_max)
    
    
    def interpolate(self, bad_value = -1):
        tec_matrix, rms_matrix = self.matrix()
        return full_binning(tec_matrix, 
                            BAD_VALUE = bad_value, 
                            max_binning = 10)





