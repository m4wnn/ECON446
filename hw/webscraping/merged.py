# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     formats: py:percent,ipynb
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.1
# ---

# %% [markdown]
"""
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
"""
# %% [markdown]
# <div style="text-align: left;">
#     <h1>Webscraping</h1>
#     <h4>Applications of Cloud Computing and Big Data - ECON 446</h3>
#     <div style="padding: 20px 0;">
#         <hr style="border: 0; height: 1px; background-image: linear-gradient(to right, rgba(0, 0, 0, 0), rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0));">
#         <p><em>Mauricio Vargas-Estrada</em><br>
#         Master Of Quantitative Economics<br>
#         University of California - Los Angeles</p>
#         <hr style="border: 0; height: 1px; background-image: linear-gradient(to right, rgba(0, 0, 0, 0), rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0));">
#     </div>
# </div>
# %% [markdown]
# ## Web Scraping Using Beautiful Soup
# %% [markdown]
# <div style="border: 1px solid black; border-radius: 5px; overflow: hidden;">
#     <div style="background-color: black; color: white; padding: 5px; text-align: left;">
#        a.) 
#     </div>
#     <div style="padding: 10px;">
#         Create a list of links for all the wikipedia pages for NYSE traded companies A-Z and 0-9.
# </div>

# %%
import requests
import string
import toolz
import pandas as pd
from rich import inspect
from bs4 import BeautifulSoup
from tqdm import tqdm
# %%
headers = {
    'Accept-Encoding': 'gzip, deflate, br',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'
}

# %%
url = lambda x: f'https://en.wikipedia.org/wiki/Companies_listed_on_the_New_York_Stock_Exchange_({x})'

# %%
def get_table_info(soup):
    links = []
    names = []
    tickers = []

    # For each row in the table of companies.
    for r in soup.find_all('tr'):
        # Get the columns for the row `r`.
        row = r.find_all('td')
        # Check if the row contains data.
        if row:
            # Extract the link of the company in the row `r`.
            tmp_link = row[0].find_all('a')
            # Check if the company has a link.
            if tmp_link:
                names.append(tmp_link[0].text)
                # Adding the root to the relative path.
                links.append('https://www.wikipedia.org' + tmp_link[0].get('href'))
                tickers.append(row[1].text.strip())
    return names, tickers, links        

# %%
links = []
names = []
tickers = []
for letter in tqdm(list(string.ascii_uppercase) + ['0-9']):
    req = requests.get(url(letter), headers=headers, timeout=20)
    # Pass if the request is not successful or time out.
    if not req.ok:
        continue
    soup = BeautifulSoup(req.content, 'html.parser')
    tmp_n, tmp_t, tmp_l= get_table_info(soup)
    links.extend(tmp_l)
    names.extend(tmp_n)
    tickers.extend(tmp_t)

# %%
companies = pd.DataFrame({'company': names, 'ticker': tickers, 'link': links})
# %%
#companies.to_csv('data/companies_links.csv', index=False)
#companies = pd.read_csv('data/companies_links.csv')
# %% [markdown]
# <div style="border: 1px solid black; border-radius: 5px; overflow: hidden;">
#     <div style="background-color: black; color: white; padding: 5px; text-align: left;">
#        b.) 
#     </div>
#     <div style="padding: 10px;">
#         Crawl through all the URLs and make 1 DF with all the NYSE publically traded companies.
# </div>
# %% [markdown]
# <div style="border: 1px solid black; border-radius: 5px; overflow: hidden;">
#     <div style="background-color: black; color: white; padding: 5px; text-align: left;">
#        c.) 
#     </div>
#     <div style="padding: 10px;">
#         What is the percetages of companies that contain 1 letter, 2 letters, 3 letters, 4 letters, 5 letters,... in the ticker (drop punctuation)?
# </div>
# %% [markdown]
# ## Web Scraping Using Beautiful Soup
# %% [markdown]
# <div style="border: 1px solid black; border-radius: 5px; overflow: hidden;">
#     <div style="background-color: black; color: white; padding: 5px; text-align: left;">
#        a.) 
#     </div>
#     <div style="padding: 10px;">
#         Using Beautiful soup .findAll method you will webscrape the front page of Reddit. Get a list of all of the "timestamps"
# </div>

# %%
URL = "https://www.reddit.com"
# %% [markdown]
# <div style="border: 1px solid black; border-radius: 5px; overflow: hidden;">
#     <div style="background-color: black; color: white; padding: 5px; text-align: left;">
#        b.) 
#     </div>
#     <div style="padding: 10px;">
#         Using the functions findChild, descendents, etc. locate the post title, text and post time into a dataframe.
# </div>
# %% [markdown]
# ## RegEx
# %% [markdown]
# <div style="border: 1px solid black; border-radius: 5px; overflow: hidden;">
#     <div style="background-color: black; color: white; padding: 5px; text-align: left;">
#        a.) 
#     </div>
#     <div style="padding: 10px;">
#         Using RegEx, get all the urls of ladder faculty profiles for UCLA Economics
# </div>

# %%
URL = "https://economics.ucla.edu/faculty/ladder"
# %% [markdown]
# <div style="border: 1px solid black; border-radius: 5px; overflow: hidden;">
#     <div style="background-color: black; color: white; padding: 5px; text-align: left;">
#        b.) 
#     </div>
#     <div style="padding: 10px;">
#         Webcrawl the links from A and use RegEx to get all the emails and phone numbers of ladder faculty profiles.
# </div>
# %% [markdown]
# ## Selenium
# %% [markdown]
# <div style="border: 1px solid black; border-radius: 5px; overflow: hidden;">
#     <div style="background-color: black; color: white; padding: 5px; text-align: left;">
#        a.) 
#     </div>
#     <div style="padding: 10px;">
#         Pick a website that has useful data to a business or economic question. Put your website you plan to scrape here : 
#         
#         https://docs.google.com/spreadsheets/d/1PJ2DOTCVCh51fn0ry1yB7qTyccR33_IXFpkYdd58MFs/edit?usp=sharing
#
#         You must have use website that no other group has. First come first serve.
# </div>

# %% [markdown]
# <div style="border: 1px solid black; border-radius: 5px; overflow: hidden;">
#     <div style="background-color: black; color: white; padding: 5px; text-align: left;">
#        b.) 
#     </div>
#     <div style="padding: 10px;">
#         Use Selenium to scrape valuable information from your website and store in a dataframe.
# </div>
# %% [markdown]
# <div style="border: 1px solid black; border-radius: 5px; overflow: hidden;">
#     <div style="background-color: black; color: white; padding: 5px; text-align: left;">
#        c.) 
#     </div>
#     <div style="padding: 10px;">
#         Write a short paragraph about the businesses or research that would use the data you scraped. Describe it's value and what it can be used for.
# </div>
