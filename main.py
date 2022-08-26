from sub_ionospheric_point import piercing_points_data
from relative_tec_calculator import relative_tec_data
from dcb_calculator import load_dcb
import pandas as pd





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
    
    #df = df.dropna(subset = ["lat", "lon", "el"])
    
    df.columns.names = [prn]
    
    
    return df



def run_for_all_prns():
    # Arapiraca
    #obs_x, obs_y, obs_z = 5043729.726, -3753105.556, -1072967.067
    
    # Belo Horizonte
    obs_x, obs_y, obs_z = 4320741.822, -4161560.476, -2161984.249

    obs = list((obs_x, obs_y, obs_z))
    
    
    path_tec = "Database/process/2015/mgbh1311.15o.txt"
    path_orbit = "Database/orbit/2015/igr18441.sp3/igr18441.sp3"
    path_dcb = "Database/dcb/2015/CAS0MGXRAP_20151310000_01D_01D_DCB.BSX"
    
    result = []
    for num in range(1, 33):
        if num < 10:
            prn = f"G0{num}"
        else:
            prn = f"G{num}"
       
  
        try: 
            df = process_data(path_tec, 
                           path_orbit, 
                           path_dcb,
                           obs, 
                           prn)
            
            df['prn'] = prn
            df.set_index('prn', append=True, inplace=True)
            result.append(df)
        except:
            continue
            print(f"In {prn} doesnt work")
    
    return pd.concat(result)
    

filename = "mgbh1311.15o"
run_for_all_prns().to_csv(f"Database/all_process/2015/{filename}.txt", 
                          sep = " ", index = True)