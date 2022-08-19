

class constants(object):
    
    def __init__(self, l1, l2, c1, p2):
        self.l1 = l1
        self.l2 = l2
        self.c1 = c1
        self.p2 = p2
        
        # Fundamental constants
        self.F1 = 1575.42e6 
        self.F2 = 1227.60e6
        self.c = 299792458.0
        
        
        self.TECU = 1.0e16 
        self.A = 40.3  
        
        self.DIFF_TEC_MAX = 0.05
        self.pmean = 0.0
        self.pdev = self.DIFF_TEC_MAX * 4.0
        
        
        # Geodesic constants
        self.alt_bottom = 6620.0
        self.alt_top = 6870.0
    
        self.radius_earth = 6371.0  
        self.avg_heigth = 250.0 
        
        self.factor_1 = (self.F1 - self.F2) / (self.F1 + self.F2) / self.c
        self.factor_2 = (self.F1 * self.F2) / (self.F2 - self.F1) / self.c 
        
        
        # Arrays com os nan's
        self.rtec_nan = ((self.l1 / self.F1) - (self.l2 / self.F2)) * self.c  
        self.mwlc_nan = (self.l1 - self.l2) - (self.F1 * self.c1 + self.F2 * self.p2) * self.factor_1