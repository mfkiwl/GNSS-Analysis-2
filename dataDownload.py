import requests 
from bs4 import BeautifulSoup 
import datetime
import os
from ultis import doy_str_format, create_directory
import zipfile




def unzipping(link, path, extension = ".14o"):
    """Extract files from zip"""
    zip_path = os.path.join(path, link)
    zip_file = zipfile.ZipFile(zip_path, 'r') 
    
    for file in zip_file.namelist():
        if file.endswith(extension):
            zip_file.extract(file, path)
            print(f"Extracting {file}")
    zip_file.close()
   
    return zip_path

def unzip_and_remove(links, complete_path):
    """Apply unzipping and try deleting"""
    for link in links:
        zip_path = unzipping(link, complete_path, 
                             extension = ".14o")
        try:
            os.remove(zip_path)
        except Exception:
            print("Could not extract files")
            
            
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
    
    rinex_path = "G:\\My Drive\\Python\\data-analysis\\GNSS\\Database\\rinex"
    year = 2014
    doy = 1
    
    station = ".zip"
    
    complete_path = create_directory(rinex_path, year, doy)
    
    links = data_download(year, doy, path = complete_path, station = station)
    
    unzip_and_remove(links, complete_path)