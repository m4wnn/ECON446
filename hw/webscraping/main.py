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
import re
import pandas as pd
import toolz
from rich import inspect
from bs4 import BeautifulSoup
from tqdm import tqdm
from multiprocessing import Pool
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
companies = companies.drop_duplicates()
# %%
print(companies.head())
# %% [markdown]
"""
<!--*!{sections/q01-b.html}-->
"""
# %%
def get_type(url):
    headers = {
        'Accept-Encoding': 'gzip, deflate, br',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'
    }
    # Crawling the wiki page of the company. Rise and exception if the url
    # is broken.
    try:
        req = requests.get(url, headers=headers, timeout=20)
    except:
        print(f'Request failed in {url}')
        return ''
    # Pass if the request is not successful or time out.
    if not req.ok:
        return ''
    soup = BeautifulSoup(req.content, 'html.parser')
    # Extracting the type of the company from the infobox vcard. Rise an
    
    try:
        vcard = soup.find_all('table', {'class': 'infobox vcard'})[0]
        comp_type = vcard.find('a', {'title': 'Public company'}).text
    except:
        print(f'No company type in {url}')
        return ''
    return comp_type
    
# %%
# Multiprocessing to crawl the websites in parallel. 
with Pool(100) as p:
    comp_type = p.map(get_type, companies['link'])

# %%
# Type of companies in lowercase.
companies['type'] = [x.lower() for x in comp_type]
# %%
# Because the format is not uniform between wikis, extract the word 'public'
# from those companies that have that pattern in their type.
pattern = re.compile(r'.*public.*')
companies['type'] = [
    pattern.sub('public', s) 
    if pattern.match(s) else s for s in companies.type
]

# %%
#companies.to_csv('data/companies_links_with_type.csv', index=False)
#companies = pd.read_csv('data/companies_links_with_type.csv')
# %%
# Companies that are public according to their wiki page.
print(companies.query("type=='public'"))
# %% [markdown]
"""
<!--*!{sections/q01-c.html}-->
"""
# %%
companies['clean_ticker'] = [
    re.match(r"[^,.!? ]+", x).group(0)
    for x in companies.ticker
]
# %%
companies['len_ticker'] = [len(x) for x in companies.clean_ticker]
# %%
len_ticker_pct = toolz.pipe(
    companies[['clean_ticker', 'len_ticker']],
    lambda x: x.drop_duplicates(),
    lambda x: x.groupby('len_ticker'),
    lambda x: x.count(),
    lambda x: x * 100 / x.sum()
)
# %%
for i, row in len_ticker_pct.iterrows():
    tmp = f'''
    -----------------------------------------
        Length of the ticker: {i}
        % in the total of companies: {row.clean_ticker:0.2f}
    -----------------------------------------
    '''
    print(tmp)
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