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
headers = {'User-Agent': user_agent_list[0]}
# %% [markdown]
"""
### Step 1: Get the HTML Content of the Website
Pull from and Explore Beautiful Soup Objects
"""
# %%
# Iterate until getting a 404 Not found Error.
#URL = lambda page: f'https://www.apartments.com/los-angeles-ca/{page}/'
URL = lambda page: f'https://www.trulia.com/CA/Los_Angeles/{page}_p/'
# %%
def response(page_number: int, URL: function) -> BeautifulSoup:
    bs_res = tz.pipe(URL(page_number),
        lambda url: requests.get(url, headers=headers),
        lambda x: BeautifulSoup(x.content, 'html.parser'),
    )
    return bs_res 
# %%
prices = tz.pipe(response,
    lambda x: x.find_all('div', attrs={'data-testid': 'property-price'}),
    lambda x: [y.text for y in x],
    lambda x: [y.replace('$', '') for y in x],
    lambda x: [y.replace(',', '') for y in x],
    lambda x: [float(y) for y in x],
)

print(prices)
# %% [markdown]
"""
Find the pricing inside of the website
"""
# %% [markdown]
"""
Clean the Prices
"""
# %% [markdown]
"""
Make a function out or it.
"""


