#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 19 18:06:14 2022

@author: shunyang.wang
"""


import os 
import sys 
import numpy as np
import pandas as pd

import grequests
import urllib.parse
from tqdm import tqdm


SERVER_URL = "http://192.168.128.240:6541/"  
# sys.argv = ['smiles.txt']

if len(sys.argv) <1:
    print('ERROR \n Usage: python query.py <smiles txt file>')
    raise Exception('Missing input option, stop...')

                    
file = sys.argv[1]
print(f'working under {file}...')   
    

with open(file,'r')as f:
    tmp = f.readlines()
f.close()

all_urls = []
for smile in tqdm(tmp):                    

    

    request_url = "{}/classify?smiles={}".format(SERVER_URL, urllib.parse.quote(smile))
    all_urls.append(request_url)
    
# Lets actually do the query and measure the speed
rs = (grequests.get(u) for u in all_urls)
responses = grequests.map(rs)

C = []
pathway = []
SC = []
glyco = []
for r in responses:
    test = r.json()  
    C.append(test['class_results'])              
    pathway.append(test['pathway_results'])
    SC.append(test['superclass_results'])
    glyco.append(test['isglycoside'])
    
    
df = pd.DataFrame({'SMILES':tmp,'pathway_results':pathway, 'superclass_results':SC, 'class_results':C, 'isglycoside':glyco })
df.to_csv(file.replace('.txt','.csv'))
                    
