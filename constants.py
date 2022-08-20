"""
Created on Wed Aug 10 15:29:00 2022

@author: Luiz

"""

class constants(object):
    
    """Contants used in the GNSS routines"""
    
    # Fundamental constants
    F1 = 1575.42e6 
    
    F2 = 1227.60e6
    c = 299792458.0
    
    
    TECU = 1.0e16 
    A = 40.3  
    
    DIFF_TEC_MAX = 0.05
    pmean = 0.0
    pdev = DIFF_TEC_MAX * 4.0
    
    
    # Geodesic constants
    alt_bottom = 6620.0
    alt_top = 6870.0

    radius_earth = 6371.0  
    avg_heigth = 250.0 
    
    factor = (F1 - F2) / (F1 + F2) / c
    factor_mw = (F1 * F2) / (F2 - F1) / c
    
    
    
    factor_TEC = ((F1 * F2) ** 2) / (F1 + F2) / (F1 - F2) / A / TECU
        
   

class factors(object):
    
    
        
    def __init__(self, 
                 l1 = None, 
                 l2 = None, 
                 c1 = None, 
                 p2 = None):
        
        
        self.l1 = l1
        self.l2 = l2
        self.c1 = c1
        self.p2 = p2
        
        const = constants()
     
        
           
     


#print(const.F1)