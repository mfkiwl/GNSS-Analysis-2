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
        
        extensions = [ext_year + "o", ext_year + "d"]
        
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
        




def URL(year, doy, typing = "IGS", const = "G"):
    
    """Build url and filenames"""
    
    week, number = gpsweek_from_doy_and_year(year, doy)
    
    url = infos[typing]

    if typing == "IGS":

        if const == "G":
            url += f"orbits/{week}/"
            filename = f"igr{week}{number}.sp3.Z"

        elif const == "R":
            url += f"glo_orbits/{week}/"
            filename = f"igl{week}{number}.sp3.Z"
        
    return filename, url


def download(url, href, path_to_save = "", 
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
                

        
def request_and_download(year, 
                         doy, 
                         path_to_save, 
                         typing = "IGS", 
                         const = "G"):
    
    """Request website and make downloads"""
    
    filename, url = URL(year, doy, typing = typing, const = const)
    
    r = requests.get(url)
    s = BeautifulSoup(r.text, "html.parser")

    parser = s.find_all('a', href = True)
    
    link_names = []

    for link in tqdm(parser, desc = f"{typing}-{const}-{doy}"):

        if filename in link:
            href = link['href']
            
            link_names.append(href)
            file = download(url, href, path_to_save)
            
            
    return link_names

    
def run_for_many_days(year = 2014, 
                      day_start = 1, 
                      day_end = 366, 
                      path_to_save = ""):
    """Running for many days in year"""
    for doy in range(day_start, day_end, 1):
       
        
        try:
            files = request_and_download(year, doy, path_to_save, 
                                     typing = "IGS", const = "R")
        except:
            continue
            print(date_from_doy(year, doy))
            
            
        unzip_and_delete(files, year, path_to_save, delete = True)
        
#C:\\Users\\Public\\Database\\orbit\\2014\\igl\\" #folder(path_to_create, root = root)