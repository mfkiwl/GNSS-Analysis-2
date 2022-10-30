import requests 
from bs4 import BeautifulSoup 
import datetime
import os
from gnss_utils import gpsweek_from_doy_and_year, date_from_doy
import zipfile
from build import paths, folder
from tqdm import tqdm    
from unlzw import unlzw


infos = {"IBGE" : 'https://geoftp.ibge.gov.br/informacoes_sobre_posicionamento_geodesico/rbmc/dados', 
         "IGS": 'https://igs.bkg.bund.de/root_ftp/IGS/products/'}

regions = {"region1": ['alar', 'bair', 'brft', 'ceeu', 
                       'ceft', 'cesb', 'crat', 'pbcg', 
                       'pbjp', 'peaf', 'pepe', 'recf',
                       'rnmo', 'rnna', 'seaj']}

def unzip_rinex(files, year, path_to_save):
    
    """Deleting after unzipping files"""
    
    zip_path = os.path.join(path_to_save, files)
    zip_file = zipfile.ZipFile(zip_path, 'r') 
    ext_year = str(year)[-2:] 
    
    extensions = [ext_year + "o", ext_year + "d"]
    
   
    zip_file = zipfile.ZipFile(zip_path, 'r') 
    
    for file in zip_file.namelist():
        
        if any(file.endswith(ext) for ext in extensions):
            
           
            zip_file.extract(file, path_to_save)
            
    zip_file.close()
    os.remove(zip_path)
        
def download(url, 
             href, 
             path_to_save = ""):
    """Function for download from link"""
    remote_file = requests.get(url + href)

    out_file = os.path.join(path_to_save, href)
    print("download...", href)
    with open(out_file, 'wb') as f:
        for chunk in remote_file.iter_content(chunk_size = 1024): 
            if chunk: 
                f.write(chunk) 
                
    return out_file

def orbit_url(year, doy, network = "IGS", const = "igr"):
    
    """Build urls and filenames from year, doy and GNSS system"""
    
    week, number = gpsweek_from_doy_and_year(year, doy)
    
    url = infos[network]

    if network == "IGS":

        if const == "igr":
            url += f"orbits/{week}/"
            filename = f"{const}{week}{number}.sp3.Z"

        elif const == "igl":
            url += f"glo_orbits/{week}/"
            filename = f"{const}{week}{number}.sp3.Z"
        
    return filename, url


def rinex_url(year, doy, network = "IBGE"):
    date = date_from_doy(year, doy)
    doy_str = date.strftime("%j")
    return f"{infos[network]}/{year}/{doy_str}/"


        
def request(url, ext = ".zip"):
    """Request website from url (RINEX or sp3)"""
    r = requests.get(url)
    s = BeautifulSoup(r.text, "html.parser")

    parser = s.find_all('a', href = True)

    return [link['href'] for link in parser if ext in link["href"]]


def filter_rinex(url, 
                 sel_stations = regions["region1"]
                 ):
  out = []
  for href in request(url):
      
      rules = [f in href for f in sel_stations]
      if any(rules):
          out.append(href)
          
  return out


def run_for_many_days(year = 2014, 
                      day_start = 1, 
                      day_end = 366, 
                      root = "D:\\"):
    
    
    """Download for whole year"""
    
    for doy in range(day_start, day_end, 1):
       
        try:
            doy
            
        except:
            print("it was not possible download...", 
                  date_from_doy(year, doy))
            continue
            
            

def download_rinex(year, 
                   doy, 
                   root = "D:\\", 
                   sel_stations = regions["region1"]):
    url = rinex_url(year, doy)
    
    path_to_create = paths(year, doy, root = root).rinex     
    path_to_save = folder(path_to_create)
    
    for href in filter_rinex(url, sel_stations = sel_stations):
        
        files = download(url, href, path_to_save)
        unzip_rinex(files, year, path_to_save)
   
def unzip_orbit(files): 
    fh = open(files, 'rb')
    compressed_data = fh.read()
    uncompressed_data = unlzw(compressed_data)
    
    str_mybytes = str(uncompressed_data)
    
    again_mybytes = eval(str_mybytes)
    decoded = again_mybytes.decode('utf8')
    
    file = open(files.replace(".Z", ""), 'w')
    file.write(decoded)
    file.close()
    fh.close()
    os.remove(files)
   
    
def download_orbit(year, doy, root = "D:\\"):
    
    for const in ["igl", "igr"]:
        fname, url = orbit_url(year, doy, 
                           network = "IGS", const = const)
    
        path_to_save = paths(year, doy, 
                             root = root).orbit(const = const)
        
        for href in request(url, ext = ".sp3"):
            if fname in href:
                files = download(url, href, path_to_save)
           
                unzip_orbit(files)

root = "C:\\"

year = 2015
doy = 2

download_rinex(year, 
                   doy, 
                   root = "D:\\", 
                   sel_stations = "")