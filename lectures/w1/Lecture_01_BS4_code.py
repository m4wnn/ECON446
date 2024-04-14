# %% [markdown]
"""
# Web Scraping with Beautiful Soup 4
## Lecture 1: Introduction to Web Scraping
"""
# %% [markdown]
"""
Write a function to web scrape the front page of “Apartments.com” Housing and get a distribution of low/high end housing costs.
"""

# %%
from bs4 import BeautifulSoup
import requests
import pandas as pd
import toolz as tz

from typing import Callable, List, Dict, Tuple, Any
# %%
# We talk about user agents later so run and ignore
user_agent_list = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36 ",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9 ",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1",
    "Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36"
] 

# %%
headers = {'User-Agent': user_agent_list[2]}
# %% [markdown]
"""
1. Get the HTML Content of the Website.
2. Find the pricing inside of the website and clean it.
3. Make a function out or it.
"""
# %%
# Iterate until getting a 404 Not found Error.
#URL = lambda page: f'https://www.apartments.com/los-angeles-ca/{page}/'
URL = lambda page: f'https://www.trulia.com/CA/Los_Angeles/{page}_p/'
# %%
def get_html(URL: Callable[[str], str], page_number: str = '') -> BeautifulSoup:
    bs_res = tz.pipe(URL(page_number),
        lambda url: requests.get(url, headers=headers),
        lambda x: BeautifulSoup(x.content, 'html.parser'),
    )
    return bs_res 
# %%
def get_prices(response: BeautifulSoup) -> List[float]:
    prices = tz.pipe(response,
        lambda x: x.find_all('div', attrs={'data-testid': 'property-price'}),
        lambda x: [y.text for y in x],
        lambda x: [y.replace('$', '') for y in x],
        lambda x: [y.replace(',', '') for y in x],
        lambda x: [float(y) for y in x],
    )
    return prices

# %%
# %%
response1 = get_html(URL, page_number='10000000000000000000000000000000000')
response2 = get_html(URL, page_number='20000000000000000000000000000000000')
response3 = get_html(URL, page_number='4')
# %%
prices1 = get_prices(response1)
prices2 = get_prices(response2)
print(prices1)
print(prices2)
# %%
# %%

def all_pages_prices(URL: Callable[[str], str], page_number: str = '') -> List[float]:
    response = get_html(URL, page_number)
    prices = get_prices(response)
    return prices