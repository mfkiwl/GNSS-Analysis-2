import numpy as np

class constants(object):
    
    """Contants used in the GNSS routines"""
    
    # Basic constants
    c = 299792458.0
    TECU = 1.0e16 
    A = 40.3  

    # Geodesic constants
    alt_bottom = 6620.0
    alt_top = 6870.0
    
    radius_earth = 6371.0  
    avg_heigth = 250.0 
        
    dtor = 0.0174533 #converte para radianos
        
    @staticmethod
    def frequency(prn):
        """Compute fundamental frequencies
           GPS: G, GLONASS: R, BEIBOU: C, Galileu: E"""
        if prn[0] == "G":
            
            F1 = 1575.42e6 
            F2 = 1227.60e6
            F5 = 1176.45e6
            
        elif prn[0] == "R":
            
            channel = [1, -4, 5, 6, 1, -4, 5, 
                       6, -2, -7, 0,-1,-2,-7,
                       0,-1,4,-3,3,2,4,-3,3,2, 
                       np.nan,-6]
            
            num = int(prn[1:]) - 1
            
            F1 = 1602e6 + channel[num] * 562.5e3
            F2 = 1246e6 + channel[num] * 437.5e3
            
        else:
            raise(f"For while doesnt have frequencies for {prn}")
            
        return F1, F2
    
   
    

        
