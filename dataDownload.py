import requests 
from bs4 import BeautifulSoup 
import datetime
import os
from gnss_utils import gpsweek_from_doy_and_year, date_from_gpsweek, date_from_doy
import zipfile
from build import paths, folder
from tqdm import tqdm    

infos = {"IBGE" : 'https://geoftp.ibge.gov.br/informacoes_sobre_posicionamento_geodesico/rbmc/dados/', 
         "IGS": 'https://igs.bkg.bund.de/root_ftp/IGS/products/'}



def unzip_and_delete(files, year, path_to_save, delete = True):
    
    """Deleting after unzipping files"""
    
    for filename in files:
       
        zip_path = os.path.join(path_to_save, filename)
        ext_year = str(year)[-2:] 
        
        extensions = [ext_year + "o", ext_year + "d", "sp3"]
        
        try:
            zip_file = zipfile.ZipFile(zip_path, 'r') 
            
            for file in zip_file.namelist():
                
                if any(file.endswith(ext) for ext in extensions):
                    zip_file.extract(file, path_to_save)
                    print(f"Extracting... {file}")
                else:
                    pass
    
            zip_file.close()
            if delete:
                try:
                    os.remove(zip_path)
                except Exception:
                    print("Could not deleting files")
        except:
            continue
        
def download(url, href, 
             path_to_save = "", 
             chunk_size = 1024):
    """Function for download from link"""
    remote_file = requests.get(url + href)
    total_length = int(remote_file.headers.get('content-length', 0))

    out_file = os.path.join(path_to_save, href)
    
    with open(out_file, 'wb') as f:
        for chunk in remote_file.iter_content(chunk_size = chunk_size): 
            if chunk: 
                f.write(chunk) 
                
    return out_file



def orbit_url(year, doy, typing = "IGS", const = "G"):
    
    """Build url and filenames"""
    
    week, number = gpsweek_from_doy_and_year(year, doy)
    
    url = infos[typing]

    if typing == "IGS":

        if const == "igr":
            url += f"orbits/{week}/"
            filename = f"{const}{week}{number}.sp3.Z"

        elif const == "igl":
            url += f"glo_orbits/{week}/"
            filename = f"{const}{week}{number}.sp3.Z"
        
    return filename, url




def check_files(year = 2014):
    for doy in range(1, 366):
        
        try:
            fname, url = orbit_url(year, 
                                   doy, 
                                   typing = "IGS", 
                                   const = "igr")
            print(fname)
        except:
            print(date_from_doy(year, doy))



def rinex_url(year, doy, network = "IBGE"):
    date = date_from_doy(year, doy)
    doy_str = date.strftime("%j")
    return f"{infos[network]}/{year}/{doy_str}/"


def create_path(year, doy, root = "C:\\"):

    date = date_from_doy(year, doy)
    doy_str = date.strftime("%j")
    
    return os.path.join(root, str(year), doy_str)


        
def request_and_download(url,
                         path_to_save, 
                         select_files = None):
    
    """Request website from url (RINEX or sp3) and download it """
    
    
    
    r = requests.get(url)
    s = BeautifulSoup(r.text, "html.parser")

    parser = s.find_all('a', href = True)

    link_names = []

    for link in parser:
       
       href = link['href']
       
       if not isinstance(select_files, list):
          select_files = [select_files] 
       
       rules = [f in href for f in select_files]
       if any(rules):
             
           link_names.append(href)
           print("download...", href)
           file = download(url, href, path_to_save)
         
            
    return link_names


def run_for_many_days(year = 2014, 
                      day_start = 1, 
                      day_end = 366, 
                      root = "D:\\"):
    
    
    """Running for whole year"""
    
    for doy in range(day_start, day_end, 1):
       
        try:
            #url = rinex_url(year, doy, network = "IBGE")
            
            fname, url = orbit_url(year, doy, 
                                   typing = "IGS", 
                                   const = "igr")
            #url = urld + fname 
            
            #print(url)
            #path_to_create = create_path(year, doy, root = root)
            #path_to_save = folder(path_to_create)
            path_to_save = paths(year, doy, root = root).orbit(const="igr")
            select_stations = ['alar', 'bair', 'brft', 'ceeu', 
                               'ceft', 'cesb', 'crat', 'pbcg', 
                               'pbjp', 'peaf', 'pepe', 'recf',
                               'rnmo', 'rnna', 'seaj']



            files = request_and_download(url,
                                         path_to_save, 
                                         select_files = fname)
            
        except:
            print("it was not possible download...", 
                  date_from_doy(year, doy))
            continue
            
            
            
        unzip_and_delete(files, year, path_to_save, delete = True)
        

root = "C:\\"

run_for_many_days(day_end = 3, root = root)




       