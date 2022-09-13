import requests 
from bs4 import BeautifulSoup 
import datetime
import os
from utils import doy_str_format, create_directory
import zipfile
from build import build_paths


            
            
def data_download(year:int, doy:int, 
                  path_to_save = "", 
                  extension = ".zip") -> list:
    """Download IBGE data"""
    
    url = f'https://geoftp.ibge.gov.br/informacoes_sobre_posicionamento_geodesico/rbmc/dados/{year}/{doy_str_format(doy)}/'

    r = requests.get(url)
    s = BeautifulSoup(r.text, "html.parser")
    
    link_names = []

    for link in s.find_all('a', href = True):

        if extension in link.text:
            href = link['href']
            print(f"Downloading {href}")
            link_names.append(href)
            
            remote_file = requests.get(url + href)
            total_length = int(remote_file.headers.get('content-length', 0))
            chunk_size = 1024
            
            with open(os.path.join(path_to_save, href), 'wb') as f:
                for chunk in remote_file.iter_content(chunk_size = chunk_size): 
                    if chunk: 
                        f.write(chunk) 
                        
    return link_names

def create_directory(path_to_create: str):
    """Create a new directory by path must be there year and doy"""
    try:
        os.mkdir(path_to_create)
        print(f"Creation of the directory {path_to_create} successfully")
    except OSError:
        print(f"Creation of the directory {path_to_create} failed")
    
    return path_to_create

def unzip_and_delete(files, year, path_to_save, delete = True):
    
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

def main():
    
    year = 2022
    doy = 1
    
    station = "alar"
    path = build_paths(year, doy)
    
    #new directory created
    path_to_save = create_directory(path.rinex)
    
    path_to_save = ""
    
    files = data_download(year, doy, 
                          path_to_save = path_to_save, 
                          extension = station)
    
    
        
    unzip_and_delete(files, year, path_to_save, delete = True)
        

main()