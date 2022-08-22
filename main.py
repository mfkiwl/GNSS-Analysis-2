from constants import *
from load import *
from sub_ionospheric_point import *
from cycle_slips import *
from relative_tec_calculator import *

        
def piercing_points_data(infile: str,     
                         obs: list, 
                         prn: str = "G01") -> pd.DataFrame:
    
    obs_x, obs_y, obs_z = obs[0], obs[1], obs[2]
    
    ob = load_orbits(infile, prn = prn)

    sat_x_vals = ob.position("x").values.ravel()
    sat_y_vals = ob.position("y").values.ravel()
    sat_z_vals = ob.position("z").values.ravel()

    times = ob.position("x").index

    lon, lat, alt = convert_coords(obs_x, obs_y, obs_z)

    result = { "lon": [], "lat": []}
    
    index = []

    for num in range(len(times)):

        sat_x, sat_y, sat_z = sat_x_vals[num], sat_y_vals[num], sat_z_vals[num]
        
        time = times[num]
        
        ip = IonosphericPiercingPoint(sat_x, sat_y, sat_z, 
                                      obs_x, obs_y, obs_z)

        elevation = ip.elevation(lat, lon)

        lat_ip, lon_ip = ip.ionospheric_sub_point(lat, lon)

        if elevation > 0:

            result['lon'].append(lon_ip)
            result['lat'].append(lat_ip)
            index.append(time)

    return pd.DataFrame(result, index = index)


def relative_tec_data(infile: str, 
                      prn: str = "G01") -> pd.DataFrame:
    
    df = pd.read_csv(infile, 
                 delim_whitespace=(True), 
                 index_col = ["sv", "time"])
    
    ob = observables(df, prn = prn)

    # Phases carriers
    l1_values, l2_values = ob.l1, ob.l2
    # Loss Lock Indicator
    l1lli_values, l2lli_values = ob.l1lli, ob.l2lli  
    # Pseudoranges
    c1_values, p2_values = ob.c1, ob.p2  

    
    time = ob.time # time
    l1, l2, rtec = cycle_slip_corrector(time, l1_values, l2_values, 
                                            c1_values, p2_values, 
                                            l1lli_values, l2lli_values)
    rtec = relative_tec(time, c1_values, 
                        p2_values, rtec)


    return pd.DataFrame({"RTEC": rtec}, index = time)


def concat_data(path_tec: str, 
                path_orbit: str, 
                path_dcb: str,
                obs: list,
                prn: str,
                time_for_interpol: str = "10min"):
    
    """Concat the relative TEC for each piercing point"""
    
    
    sat_bias = sat_bias_corrector(infile, prn = prn)

    
    tecData = relative_tec_data(path_tec, prn = prn)
    
    tecData["cTEC"] = tecData["RTEC"] - sat_bias
    
    ippData = piercing_points_data(path_orbit, obs, prn = prn)
    
    df = pd.concat([tecData, ippData], axis = 1)
    
    if time_for_interpol:
        df = df.resample(time_for_interpol).asfreq(
            ).interpolate().ffill().bfill()
    
        return df
    
    else:
        return df.dropna()




def main():
    
    obs_x, obs_y, obs_z = 5043729.726, -3753105.556, -1072967.067

    obs = list((obs_x, obs_y, obs_z))
    prn = "G01"
    path_tec = "Database/alar0011.14o.txt"
    path_orbit = "Database/jpl17733.sp3/igr17733.sp3"
    path_dcb = "Database/dcb/2014/CAS0MGXRAP_20140010000_01D_01D_DCB.BSX"

    '''
    df = concat_data(path_tec, 
                     path_orbit, 
                     obs, prn, 
                     time_for_interpol = None)
    '''
   
    
    
    df = relative_tec_data(path_tec)
    
    print(df)
    
    
main()
