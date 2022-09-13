import requests 
from bs4 import BeautifulSoup 
import datetime
import os
from utils import doy_str_format, create_directory
import zipfile
from build import build_paths




def unzipping(link, path, extension = ".14o"):
    
    """Extract files from zip"""
    
    zip_path = os.path.join(path, link)
    
    try:
        zip_file = zipfile.ZipFile(zip_path, 'r') 
        
        for file in zip_file.namelist():
            if file.endswith(extension):
                zip_file.extract(file, path)
                print(f"Extracting {file}")
            else:
                print(f"Could not extract the {file}")
                
        zip_file.close()
    except:
        print("Bad zip file")
    
    return zip_path

def unzip_and_remove(links, complete_path, delete = False, 
                     extension = ".22d"):
    """Apply unzipping and try deleting"""
    for link in links:
        zip_path = unzipping(link, complete_path, 
                             extension = extension)
        print(f"Unzipping {link}")
        if delete:
            try:
                os.remove(zip_path)
            except Exception:
                print("Could not deleting files")
            
            
def data_download(year, doy, path = "", station = ".zip"):
    """Download IBGE data"""
    
    url = f'https://geoftp.ibge.gov.br/informacoes_sobre_posicionamento_geodesico/rbmc/dados/{year}/{doy_str_format(doy)}/'

    r = requests.get(url)
    s = BeautifulSoup(r.text, "html.parser")
    
    link_names = []

    for link in s.find_all('a', href = True):

        if station in link.text:
            href = link['href']
            print(f"Downloading {href}")
            link_names.append(href)
            remote_file = requests.get(url + href)
            total_length = int(remote_file.headers.get('content-length', 0))
            chunk_size = 1024
            
            with open(os.path.join(path, href), 'wb') as f:
                for chunk in remote_file.iter_content(chunk_size = chunk_size): 
                    if chunk: 
                        f.write(chunk) 
                        
    return link_names

def main():
    
    year = 2022
    doy = 1
    
    station = ".zip"
    
    rinex_path = os.path.join(build_paths(year, doy).current_path, "rinex")
        
    #complete_path = create_directory(rinex_path, year, doy)
    
    #links = data_download(year, doy, 
    #                      path = complete_path, 
    #                      station = station)
    
    complete_path = build_paths(year, doy).rinex
    _, _, files = next(os.walk(complete_path))
     
    unzip_and_remove(files, complete_path, delete = True, extension = ".22d")
    
main()