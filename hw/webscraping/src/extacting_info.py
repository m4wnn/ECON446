# %%
import numpy as np
import pickle as pkl
import os
import re
import pandas as pd
from bs4 import BeautifulSoup
from rich import inspect
# %%
PROJECT_PATH = os.path.join(
    '/home', 'm4wnn', 'Documents', 'GitHub', 'ECON446', 'hw', 'webscraping' 
)
FILES_PATH = os.path.join(
    PROJECT_PATH, 'data', 'neighborhoods_around_ucla'
)
# %% Joining the information for each neighborhood.
raw = []
ngh = []

re_ngh = re.compile(r'\S+(?=_results\.pkl)')

for file in os.listdir(FILES_PATH):
    tmp_file = os.path.join(FILES_PATH, file)
    
    with open(tmp_file, 'rb') as f:
        tmp_info = pkl.load(f)
    
    raw.extend(tmp_info)
    ngh.extend(re_ngh.findall(file) * len(tmp_info))
# %%
raw_soup = [BeautifulSoup(x, 'html.parser') for x in raw]
# %%
rent = [
    x.find('div', {'data-testid':'card-price'}).text
    for x in raw_soup
]
# %%
rent_min = [
    re.findall(r'(?<=^\$)\d+,\d+(?=$|\s\-)', x)
    for x in rent
]
rent_min = [x[0] if x else '' for x in rent_min]
rent_min = [x.replace(',', '') if x != '' else '' for x in rent_min]
rent_min = [float(x) if x != '' else np.nan for x in rent_min]
# %%
rent_max = [
    re.findall(r'(?<=\s\-\s\$)\d+,\d+', x)
    for x in rent
]
rent_max = [x[0] if x else '' for x in rent_max]
rent_max = [x.replace(',', '') if x != '' else '' for x in rent_max]
rent_max = [float(x) if x != '' else np.nan for x in rent_max]
# %%
n_beds = [
    x.find('li', {'data-testid':'property-meta-beds'})
    for x in raw_soup
]
n_beds = [x.text if x else '' for x in n_beds]
# %%
n_beds_min = [
    re.findall(r'(?<=^)(\d+|Studio)', x)
    for x in n_beds
]
n_beds_min = [x[0] if x else np.nan for x in n_beds_min]
# %%
n_beds_max = [
    re.findall(r'(?<=\-\s)\d+', x)
    for x in n_beds
]
n_beds_max = [x[0] if x else np.nan for x in n_beds_max]
# %%
n_baths = [
    x.find('li', {'data-testid':'property-meta-baths'})
    for x in raw_soup
]
n_baths = [x.text if x else '' for x in n_baths]
# %%
n_baths_min = [
    re.findall(r'(?<=^)\d+', x)
    for x in n_baths
]
n_baths_min = [x[0] if x else np.nan for x in n_baths_min]
n_baths_min = [float(x) if x != np.nan else np.nan for x in n_baths_min]
# %%
n_baths_max = [
    re.findall(r'(?<=\-\s)\d+', x)
    for x in n_baths
]
n_baths_max = [x[0] if x else np.nan for x in n_baths_max]
n_baths_max = [float(x) if x != np.nan else np.nan for x in n_baths_max]
# %%
area = [
    x.find('li', {'data-testid':'property-meta-sqft'})
    for x in raw_soup
]
area = [x.text if x else '' for x in area]
area =[
    re.findall(r'(?<=sqft).+(?=\ssquare\sfeet)', x)
    if x != '' else [] for x in area

]
area = [x[0] if x else '' for x in area]
# %%
area_min = [
    re.findall(r'(?<=^)(\d{3}|\d+,\d+)', x)
    for x in area
]
area_min = [x[0] if x else '' for x in area_min]
area_min = [x.replace(',', '') if x != '' else '' for x in area_min]
area_min = [float(x) if x != '' else np.nan for x in area_min]
# %%
area_max = [
    re.findall(r'(?<=\-\s)(\d{3}|\d+,\d+)', x)
    for x in area
]
area_max = [x[0] if x else '' for x in area_max]
area_max = [x.replace(',', '') if x != '' else '' for x in area_max]
area_max = [float(x) if x != '' else np.nan for x in area_max]
# %%
addss_1 = [
    x.find('div', {'data-testid':'card-address-1'})
    for x in raw_soup
]
addss_1 = [x.text if x else '' for x in addss_1]
# %%
addss_2 = [
    x.find('div', {'data-testid':'card-address-2'})
    for x in raw_soup
]
addss_2 = [x.text if x else '' for x in addss_2]
# %%
data = pd.DataFrame({
    'neighborhood': ngh,
    'rent_min': rent_min,
    'rent_max': rent_max,
    'n_beds_min': n_beds_min,
    'n_beds_max': n_beds_max,
    'n_baths_min': n_baths_min,
    'n_baths_max': n_baths_max,
    'area_min': area_min,
    'area_max': area_max,
    'address_1': addss_1,
    'address_2': addss_2
})
# %%
data.loc[data.rent_max.isna(), 'rent_max'] = data.loc[data.rent_max.isna(), 'rent_min']
# %%
data.loc[data.n_beds_max.isna(), 'n_beds_max'] = data.loc[data.n_beds_max.isna(), 'n_beds_min']
# %%
data.loc[data.n_baths_max.isna(), 'n_baths_max'] = data.loc[data.n_baths_max.isna(), 'n_baths_min']
# %%
data.loc[data.area_max.isna(), 'area_max'] = data.loc[data.area_max.isna(), 'area_min']
# %%
data.to_csv(os.path.join(FILES_PATH, '..', 'neighborhoods_around_ucla.csv'), index=False)