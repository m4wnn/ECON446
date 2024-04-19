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
import toolz
import time
import pickle
import pandas as pd
import numpy as np

from bs4 import BeautifulSoup
from multiprocessing import Pool
from tqdm import tqdm
from rich import inspect
from pprint import pprint

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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
# Cleaning the ticker column.
companies['clean_ticker'] = [
    re.match(r"[^,.!? ]+", x).group(0)
    for x in companies.ticker
]
# %%
# Calculating the length of the ticker.
companies['len_ticker'] = [len(x) for x in companies.clean_ticker]
# %%
# Counting the percentage of companies with each length of ticker.
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
# User agent to simulate a browser in selenium.
options = Options()
options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")

# %%
# Initialize the browser.
driver = webdriver.Firefox(options=options)
# %%
# Open the website in the browser.
driver.get("https://www.reddit.com")
time.sleep(5)

# Verifying the numbers of posts extracted from the page.
num_posts_before = 0

# posts inside the website to scroll down.
body = driver.find_element(By.TAG_NAME, 'body')

start_time = time.time()
time_limit_scroll = 600 # 10 minutes

# Scrolling down the page until the time limit is reached.
print('Scrolling down the page...')
while time.time() - start_time < time_limit_scroll:
    print(f'Time elapsed: {time.time() - start_time:.2f} seconds')
    # Extracting the articles from the page.
    posts = driver.find_elements(By.XPATH, '//article[@class="w-full m-0"]')
    
    # Verifying that the number of posts is changing in each iteration.
    if len(posts) == num_posts_before:
        print('Something went wrong. The number of posts is not changing. Stopping..')
        break  
    else:
        num_posts_before = len(posts)

    # Simulate pressing the END key to scroll down the page.
    body.send_keys(Keys.END)

    # Wait for the page to load.
    time.sleep(6)
print('Time limit reached.')
# %%
# Extracting the html for each post.
html_content = [x.get_attribute('outerHTML') for x in posts]
 
# %%
# Save the html content to a pickle file.
with open('data/reddit_posts.pkl', 'wb') as f:
    pickle.dump(html_content, f)

# %%
# Close the browser.
driver.quit()

# %%
# Load the html content from the pickle file to avoid running the code again.
#with open('data/reddit_posts.pkl', 'rb') as f:
    #html_content = pickle.load(f)

# %%
# Parsing each post with BeautifulSoup.
html_content = [BeautifulSoup(x, 'html.parser') for  x in html_content]
# %%
# Extracting only the timestamps for each post.
timestamps = [x.find('time').get_attribute_list('datetime')[0] for x in html_content]
# %%
print(f'Total number of posts extracted: {len(timestamps)}')
print('First 10 timestamps:')
pprint(timestamps[0:9])
# %% [markdown]
"""
<!--*!{sections/q02-b.html}-->
"""
# %%
titles = [x.find('article').get_attribute_list('aria-label')[0] for x in html_content]
# %%
text_div_class = re.compile(r'.*feed-card-text-preview.*')
texts = []
for post in html_content:
    tmp = post.find_all(
        'div',
        class_ = lambda x : x and text_div_class.match(x)    
    )
    if tmp:
        tmp = tmp[0].text
    else:
        tmp = np.nan
    texts.append(tmp)
# %%
post_df = pd.DataFrame({
    'timestamp': timestamps,
    'title': titles,
    'text': texts
})

# %%
# Printing the first 10 posts with text.
print('First 5 posts with text:')
print(post_df.query('text.notna()').head(5))
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