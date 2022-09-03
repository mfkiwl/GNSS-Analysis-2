# -*- coding: utf-8 -*-
"""
Created on Sat Sep  3 18:26:03 2022

@author: Luiz
"""
import requests 
from bs4 import BeautifulSoup 


def data_download(year, doy, path = "", station = ".zip"):
    
    url = f'https://geoftp.ibge.gov.br/informacoes_sobre_posicionamento_geodesico/rbmc/dados/{year}/00{doy}'

    r = requests.get(url)
    s = BeautifulSoup(r.text, "html.parser")
    

    for link in s.find_all('a', href = True):

        if station in link.text:
            href = link['href']
            print(href)
            remote_file = requests.get(url + href)
            total_length = int(remote_file.headers.get('content-length', 0))
            chunk_size = 1024

            with open(path + href, 'wb') as f:
                for chunk in remote_file.iter_content(chunk_size = chunk_size): 
                    if chunk: 
                        f.write(chunk)    