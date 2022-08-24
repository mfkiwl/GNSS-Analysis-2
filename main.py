from sub_ionospheric_point import piercing_points_data
from relative_tec_calculator import relative_tec_data
from dcb_calculator import load_dcb
        





def process_data(path_tec: str, 
                path_orbit: str, 
                path_dcb: str,
                obs: list,
                prn: str):
    
    """
    Concat the relative TEC for each piercing point 
    and compute other variables
    """
    
    
    sat_bias = load_dcb(path_dcb).value_tec

    tecData = relative_tec_data(path_tec, prn = prn)
    
    tecData["cTEC"] = tecData["rTEC"] - sat_bias
      
    ippData = piercing_points_data(path_orbit, obs, prn = prn)
    
    
    df = tecData.join(ippData).interpolate()
    
    df["vTEC"] = df["proj"] * df["cTEC"]
    
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

    
    sat_bias = load_dcb(path_dcb).value_tec

    tecData = relative_tec_data(path_tec, prn = prn)
  
   
    df = process_data(path_tec, 
                       path_orbit, 
                       path_dcb,
                       obs, 
                       prn)
    
    print(df)
    

    df.to_csv("test.txt", sep = " ", index = True)
    
main()
