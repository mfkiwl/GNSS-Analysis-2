import gnsscal
import datetime
import os
import numpy as np

def date_from_doy(year: int, doy:int) -> datetime.datetime:
    """Return date from year and doy"""
    return datetime.date(year, 1, 1) + datetime.timedelta(doy - 1)

def gpsweek_from_date(date: datetime.datetime) -> tuple:
    """Return GPS week and number from date"""
    return gnsscal.date2gpswd(date)

def gpsweek_from_doy_and_year(year: int, doy:int) -> tuple:
    """Return GPS week and number from date"""
    return gnsscal.date2gpswd(date_from_doy(year, doy))

def doy_from_gpsweek(week: int, number: int) -> tuple:
    """Return year and doy from gps week"""
    return gnsscal.gpswd2yrdoy(week, number)

def date_from_gpsweek(week: int, number:int) -> datetime.date:
    """Return date from gps week"""
    year, doy = doy_from_gpsweek(week, number)
    return date_from_doy(year, doy)

def day_and_month(year: int, doy:int) -> tuple:
    """Get month and day from year and doy"""
    date = date_from_doy(year, doy)
    return date.month, date.day
        
def delete_files(infile, extension = ".22d"):
    """Deleting files in directory by extension"""
    _, _, files = next(os.walk(infile))
    
    for filename in files:
        if filename.endswith(extension):
            try:
                os.remove(os.path.join(infile, filename))
            except Exception:
                print(f"Could not delete {filename}")

    
def tec_fname(filename: str) -> datetime.datetimw:
    """Convert TEC filename (EMBRACE format) to datetime"""
    args = filename.split('_')
    date = args[1][:4] + '-' + args[1][4:6]+ '-' +args[1][-2:] 
    time = args[-1].replace('.txt', '')
    time = time[:2] + ':' + time[2:]
    
    return datetime.datetime.strptime(date + ' ' + time, "%Y-%m-%d %H:%M")

def replace_values(list_to_replace: list, 
                   item_to_replace: str = "", 
                   item_to_replace_with: float = np.nan)-> list:
    """Replace values in list"""
    return [item_to_replace_with if item == item_to_replace 
            else item for item in list_to_replace]


def remove_values(list_to_remove: list, 
                  item_to_remove:str = "") -> list:
    """Remove value in list"""
    return [item.strip() for item in list_to_remove if item != ""]

def find(s: str, ch: str) -> int:
    return [i for i, ltr in enumerate(s) if ltr == ch]

def sep_elements(list_to_sep:list, length:int = 16) -> list:
    """Split elements by length"""
    return [list_to_sep[num: num + length].strip() for num in 
            range(0, len(list_to_sep), length)]


class fname_attrs(object):
    
    """Attributes of filenames (rinex, orbit and bias)"""
    
    def __init__(self, fname):
        
        extension = fname.split(".")
        if extension[1][-1] == "o":
        
            self.station = extension[0][:4]
            year = extension[1][:2]
            doy = extension[0][4:7]

            if int(year) < 99:
                year = "20" + year
            else:
                year = "19" + year

            self.year = int(year)
            self.doy = int(doy)
            
        elif extension[1] == "sp3":
            
            self.const = extension[0][:3]
            week = int(extension[0][3:7])
            number = int(extension[0][7:])
            
            self.year, self.doy = doy_from_gpsweek(week, number)
            
        else:
            args = extension[0].split("_")

            if "MGX" in args[0]:
                self.year = int(args[1][:4])
                self.doy = int(args[1][4:7])
    
    @property
    def date(self):
        return date_from_doy(self.year, self.doy)
         
    
def main():
   
    
    infile = "D:/database/orbit/2014/igl/"
    
    _, _, files = next(os.walk(infile))

    dates_igl = [fname_attrs(filename).date for filename in files]
    print(dates_igl)
    
    
        
        
