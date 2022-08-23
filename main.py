from constants import *
from load import *
from sub_ionospheric_point import *
from cycle_slips import cycle_slip_corrector
from relative_tec_calculator import relative_tec
from dcb_calculator import sat_bias_corrector
        
def piercing_points_data(orbital_path: str,     
                         obs: list, 
                         prn: str = "G01") -> pd.DataFrame:
    """Read orbits files fpr each prn and compute the ionospheric 
    Piercing point (given by latitude and longitude)"""
    ox, oy, oz = obs[0], obs[1], obs[2]
    
    df = load_orbits(orbital_path, prn = prn).position()

    sat_x_vals = df.x.values
    sat_y_vals = df.y.values
    sat_z_vals = df.z.values

    times = df.index

    lon, lat, alt = convert_coords(ox, oy, oz)

    result = { "lon": [], "lat": [], "el": []}
    
    index = []

    for num in range(len(times)):

        sx, sy, sz = df.x.values[num], df.y.values[num], df.z.values[num]
        
        time = times[num]
        
        ip = IonosphericPiercingPoint(sx, sy, sz, ox, oy, oz)

        elevation = ip.elevation(lat, lon)

        lat_ip, lon_ip = ip.ionospheric_sub_point(lat, lon)

        result['lon'].append(lon_ip)
        result['lat'].append(lat_ip)
        result["el"].append(elevation)
        index.append(time)

    return pd.DataFrame(result, index = index)


def relative_tec_data(infile: str, 
                      prn: str = "G01") -> pd.DataFrame:
    """
    Read rinex pre-process files (already missing values removed), 
    correcter cycle-slip and compute the relative tec
    """
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
    
    
    l1, l2, rtec = cycle_slip_corrector(time, 
                                        l1_values, l2_values, 
                                        c1_values, p2_values, 
                                        l1lli_values, l2lli_values)
    rtec = relative_tec(time, c1_values, 
                        p2_values, rtec)


    return pd.DataFrame({"rTEC": rtec}, index = time)


def process_data(path_tec: str, 
                path_orbit: str, 
                path_dcb: str,
                obs: list,
                prn: str):
    
    """
    Concat the relative TEC for each piercing point 
    and compute other variables
    """
    
    
    #sat_bias = sat_bias_corrector(path_dcb, prn = prn)

    tecData = relative_tec_data(path_tec, prn = prn)
    
    #tecData["cTEC"] = tecData["rTEC"] - sat_bias
      
    ippData = piercing_points_data(path_orbit, obs, prn = prn)
    
    
    df = tecData.join(ippData).interpolate()
    
    df["vTEC"] = TEC_projection(df["el"]) * df["rTEC"]
    
    df = df.dropna(subset = ["lat", "lon", "el"])
    
    df.columns.names = [prn]
    
    return df



def main():
    
    obs_x, obs_y, obs_z = 5043729.726, -3753105.556, -1072967.067

    obs = list((obs_x, obs_y, obs_z))
    
    prn = "G01"
    #path_tec = "Database/alar0011.14o.txt"
    #path_orbit = "Database/jpl17733.sp3/igr17733.sp3"
    #path_dcb = "Database/dcb/2014/CAS0MGXRAP_20140010000_01D_01D_DCB.BSX"
    
    path_tec = "alar0011.22o.txt"
    path_orbit = "igr21906.sp3"
    path_dcb = "CAS0MGXRAP_20220010000_01D_01D_DCB.BSX"

    
    df1 = process_data(path_tec, 
                     path_orbit, 
                     path_dcb,
                     obs, prn)
  
   
    #df[["vTEC", "rTEC", "cTEC"]].plot()
    

    df1.to_csv("test.txt", sep = " ", index = True)
    
    

main()
