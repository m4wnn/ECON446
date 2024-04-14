# %% [markdown]
"""
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
"""
# %% [markdown]
"""
<!--*!{misc/title.html}-->
"""
# %% [markdown]
"""
<!--*!{sections/q01.md}-->
"""
# %% [markdown]
"""
<!--*!{sections/q01-a.html}-->
"""

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
"""
<!--*!{sections/q01-b.html}-->
"""
# %% [markdown]
"""
<!--*!{sections/q01-c.html}-->
"""
# %% [markdown]
"""
<!--*!{sections/q02.md}-->
"""
# %% [markdown]
"""
<!--*!{sections/q02-a.html}-->
"""

# %%
URL = "https://www.reddit.com"
# %% [markdown]
"""
<!--*!{sections/q02-b.html}-->
"""
# %% [markdown]
"""
<!--*!{sections/q03.md}-->
"""
# %% [markdown]
"""
<!--*!{sections/q03-a.html}-->
"""

# %%
URL = "https://economics.ucla.edu/faculty/ladder"
# %% [markdown]
"""
<!--*!{sections/q03-b.html}-->
"""
# %% [markdown]
"""
<!--*!{sections/q04.md}-->
"""
# %% [markdown]
"""
<!--*!{sections/q04-a.html}-->
"""

# %% [markdown]
"""
<!--*!{sections/q04-b.html}-->
"""
# %% [markdown]
"""
<!--*!{sections/q04-c.html}-->
"""