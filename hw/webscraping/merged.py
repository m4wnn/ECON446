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
#         <p><em>Bella Rakhlina</em><br>
#         <em>Lora Yovcheva</em><br>
#         <em>Mauricio Vargas-Estrada</em><br>
#         <br>Master Of Quantitative Economics<br>
#         University of California - Los Angeles</p>
#         <hr style="border: 0; height: 1px; background-image: linear-gradient(to right, rgba(0, 0, 0, 0), rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0));">
#     </div>
# </div>
# %%
import requests
import string
import re
import toolz
import time
import pickle
import pandas as pd
import numpy as np
import os
import random

from bs4 import BeautifulSoup
from multiprocessing import Pool
from tqdm import tqdm
from rich import inspect
from pprint import pprint

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

from stem import Signal
from stem.control import Controller

import tbselenium.common as cm
from tbselenium.utils import launch_tbb_tor_with_stem
from tbselenium.tbdriver import TorBrowserDriver

import pickle as pkl
# %% [markdown]
# ## Web Crawling Tables
# %% [markdown]
# <div style="border: 1px solid black; border-radius: 5px; overflow: hidden;">
#     <div style="background-color: black; color: white; padding: 5px; text-align: left;">
#        a.) 
#     </div>
#     <div style="padding: 10px;">
#         Create a list of links for all the wikipedia pages for NYSE traded companies A-Z and 0-9.
# </div>

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
# <div style="border: 1px solid black; border-radius: 5px; overflow: hidden;">
#     <div style="background-color: black; color: white; padding: 5px; text-align: left;">
#        b.) 
#     </div>
#     <div style="padding: 10px;">
#         Crawl through all the URLs and make 1 DF with all the NYSE publically traded companies.
# </div>
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
# <div style="border: 1px solid black; border-radius: 5px; overflow: hidden;">
#     <div style="background-color: black; color: white; padding: 5px; text-align: left;">
#        c.) 
#     </div>
#     <div style="padding: 10px;">
#         What is the percetages of companies that contain 1 letter, 2 letters, 3 letters, 4 letters, 5 letters,... in the ticker (drop punctuation)?
# </div>
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
# <div style="border: 1px solid black; border-radius: 5px; overflow: hidden;">
#     <div style="background-color: black; color: white; padding: 5px; text-align: left;">
#        b.) 
#     </div>
#     <div style="padding: 10px;">
#         Using the functions findChild, descendents, etc. locate the post title, text and post time into a dataframe.
# </div>
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

# %%
# Getting the flex table of the ladder faculty.
req_ladder = requests.get(URL, headers=headers)

# %%
# Extracting the name and url for each profile in the ladder faculty.
tmp = re.compile(r'flex_column av_one_fourth.*')
profiles_info = toolz.pipe(
    req_ladder,
    lambda x: x.content,
    lambda x: BeautifulSoup(x, 'html.parser'),
    lambda x : x.find(
        'div',
        {'id': 'wpv-view-layout-974-CATTR0494cfbfb8d3e1b3152203680573333f'}
    ),
    lambda x: x.find_all(
        'div',
        class_ = lambda x : x and tmp.match(x)
    ),
    lambda x: [y.find('h3') for y in x],
    lambda x: {
        'name': [y.text for y in x],
        'url': [y.find('a')['href'] for y in x]
    },
    lambda x: pd.DataFrame(x)
)
# %% [markdown]
# <div style="border: 1px solid black; border-radius: 5px; overflow: hidden;">
#     <div style="background-color: black; color: white; padding: 5px; text-align: left;">
#        b.) 
#     </div>
#     <div style="padding: 10px;">
#         Webcrawl the links from A and use RegEx to get all the emails and phone numbers of ladder faculty profiles.
# </div>
# %%
# Crawling the profiles urls.
crawled_info = []
for url in tqdm(profiles_info['url']):
    tmp = requests.get(url, headers=headers).content
    crawled_info.append(tmp)
    time.sleep(10)
# %%
# Extracting the email and phone from the crawled info using regex.
regex_email = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
regex_phone = re.compile(r'([\+]?[(]?[0-9]{3}[)]?[-\s\.][0-9]{3}[-\s\.][0-9]{4,6})')
email = []
phone = []
for raw in crawled_info:
    tmp = BeautifulSoup(raw, 'html.parser')
    tmp_email = tmp.find(string=regex_email)
    tmp_phone = tmp.find(string=regex_phone)

    if tmp_email:
        email.append(tmp_email)
    else:
        email.append(np.nan)
    
    if tmp_phone:
        phone.append(tmp_phone)
    else:
        phone.append(np.nan)

# %%
profiles_info['email'] = email
profiles_info['phone'] = phone
# %%
# Printing those profiles with phone number.
print(profiles_info.query('phone.notna()').head(10))
# %%
tmp = f"""
Number of profiles: {profiles_info.shape[0]}
Number of profiles with phone number: {profiles_info.query('phone.notna()').shape[0]}
"""
print(tmp)
# %% [markdown]
# ## Selenium
# %% [markdown]
# <div style="border: 1px solid black; border-radius: 5px; overflow: hidden;">
#     <div style="background-color: black; color: white; padding: 5px; text-align: left;">
#        a.) 
#     </div>
#     <div style="padding: 10px;">
#         <p>Pick a website that has useful data to a business or economic question. Put your website you plan to scrape here:</p>
#         <p>https://docs.google.com/spreadsheets/d/1PJ2DOTCVCh51fn0ry1yB7qTyccR33_IXFpkYdd58MFs/edit?usp=sharing</p>
#         <p>You must have use website that no other group has. First come first serve.</p>
# </div>
# %% [markdown]
"""
The selected website, [www.realtor.com](https://www.realtor.com/), offers listings for properties for sale and rent, including those around the UCLA campus, which is our area of interest. We are particularly focused on gathering rental information from the following neighborhoods:

- Bel Air
- Brentwood
- Culver City
- Encino
- Mar Vista
- Mid Wilshire
- Pacific Palisades
- Palms
- Playa del Rey
- Playa Vista
- Santa Monica
- Sawtelle
- Sherman Oaks
- Studio City
- Venice
- West Los Angeles
- Westwood

To facilitate webscraping, we are integrating `Selenium` with `Tor`. The following code snippet is utilized to extract the required information from the website.
"""
# %% [markdown]
# <div style="border: 1px solid black; border-radius: 5px; overflow: hidden;">
#     <div style="background-color: black; color: white; padding: 5px; text-align: left;">
#        b.) 
#     </div>
#     <div style="padding: 10px;">
#         Use Selenium to scrape valuable information from your website and store in a dataframe.
# </div>
# %%
def save_data(data, filename):
    script_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_directory, filename)
    with open(file_path, 'wb') as file:
        pkl.dump(data, file)
    print(f"Data saved to {file_path}")
# %%
def random_sleep(minimum=2, maximum=5):
    """Generate a random sleep time to mimic human behavior."""
    time.sleep(random.uniform(minimum, maximum))

# %%
def human_like_scroll(driver):
    """Simulate human-like scrolling behavior more slowly."""
    total_height = driver.execute_script("return document.body.scrollHeight")
    current_scroll_position = 0
    increment = total_height / 20  # Divide the scroll into smaller steps

    while current_scroll_position <= total_height:
        # Scroll down to the next increment
        driver.execute_script(f"window.scrollTo(0, {current_scroll_position});")
        current_scroll_position += increment

        # Wait a random time between scrolls to mimic human behavior
        time.sleep(random.uniform(0.5, 3))  # Adjust timing as needed

    # Finally, scroll to the very bottom to ensure all lazy loaded items are triggered
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(random.uniform(15, 20))  # A final pause at the bottom

# %%
def switch_tor_circuit():
    """Use Stem to switch Tor circuit."""
    with Controller.from_port(port=9251) as controller:
        controller.authenticate()
        controller.signal(Signal.NEWNYM)
# %%
def get_tor_version():
    try:
        with Controller.from_port(port=9251) as controller:
            controller.authenticate()  # Asume que no se necesita contraseña
            version = controller.get_version()
            print("Connected to Tor version:", version)
    except Exception as e:
        print(f"Error connecting to Tor control port: {e}")

# %%
def get_current_circuit():
    """Retrieve and print the current Tor circuit."""
    try:
        with Controller.from_port(port=9251) as controller:
            controller.authenticate()  # Assumes no password is needed
            for circ in controller.get_circuits():
                if circ.status == 'BUILT':
                    print("Circuit ID: {}".format(circ.id))
                    print("Circuit Path:")
                    for i, entry in enumerate(circ.path):
                        desc = controller.get_network_status(entry[0], None)
                        fingerprint, nickname = entry
                        address = desc.address if desc else 'unknown'
                        print(f"  {i+1}: {nickname} ({fingerprint}) at {address}")
                    print("\n")
                    break  # Just show the first 'BUILT' circuit
    except Exception as e:
        print(f"Error retrieving current circuit: {e}")
# %%
def zipcode_scrapping(zipcode):
    tor_path = '/home/m4wnn/tor-browser-linux-x86_64-13.0.14/tor-browser'
    while True:
        try:
            tor_process = launch_tbb_tor_with_stem(tbb_path=tor_path)
            break
        except Exception as e:
            print(f"Error initializing Tor process: {e}")
            print("Retrying to initialize.")
    print("Tor process initialized.")
            

    ## Setting a random user-agent using pref_dict
    user_agent_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
        "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"
    ]

    random_user_agent = random.choice(user_agent_list)
    pref_dict = {"general.useragent.override": random_user_agent}

    # Create a TorBrowserDriver instance with customized user-agent
    try:
        driver = TorBrowserDriver(
            tor_path,
            tor_cfg=cm.USE_STEM,
            pref_dict=pref_dict,
            headless=True
        )
    except Exception as e:
        print(f"Error creating TorBrowserDriver: {e}")
        return []
    
    time.sleep(3)
    #driver.get(f'https://www.realtor.com/realestateandhomes-search/{zipcode}')
    driver.get(f'https://www.realtor.com/apartments/{zipcode}')
    tmp_current_url = driver.current_url
    print(tmp_current_url)
    
    random_sleep(5, 10)
    
    
    
    regex_property = re.compile(r'placeholder_property_\d*')
    property_info = []
    try:
        refresh_count = 0
        while True:
            human_like_scroll(driver)

            try:
                property_section = driver.find_element(
                    By.CSS_SELECTOR,
                    'section[class^="PropertiesList_propertiesContainer"]'
                )
                section_content = BeautifulSoup(
                    property_section.get_attribute('innerHTML'),
                    'html.parser'
                )

                properties = section_content.find_all(
                    'div',
                    id=lambda x: x and regex_property.match(x)
                )
                
                property_htmls = [str(prop) for prop in properties]
                property_info.extend(property_htmls)
                

            except NoSuchElementException:
                if refresh_count == 2:
                    print("Refreshing limit reached. Exiting loop.")
                    break
                print("Property section not found.")
                print("Changing circuit.")
                switch_tor_circuit()
                print("Refreshing Website.")
                refresh_count += 1
                driver.refresh()
                continue 
            
            refresh_count = 0
            try:
                tmp_current_url = driver.current_url
                switch_tor_circuit()  # Switch Tor circuit before loading the page
                time.sleep(15)  # Wait for the new circuit to be established
                next_button = driver.find_element(By.LINK_TEXT, "Next")
                next_button.click()
                random_sleep(3, 6)
                tmp_new_url = driver.current_url
                if tmp_current_url == tmp_new_url:
                    print("Same page detected. Exiting loop.")
                    break
                print(tmp_new_url)
            except NoSuchElementException:
                print("Next button not found. Exiting loop.")
                break

    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        driver.quit()
        tor_process.kill()

    return property_info
# %%
neighborhoods = [
    'Bel-Air_Los-Angeles_CA',
    'Brentwood_Los-Angeles_CA',
    'Culver-City_CA',
    'Encino_Los-Angeles_CA',
    'Mar-Vista_Los-Angeles_CA',
    'Mid-Wilshire_Los-Angeles_CA',
    'Pacific-Palisades_Los-Angeles_CA',
    'Palms_Los-Angeles_CA',
    'Playa-del-Rey_Los-Angeles_CA',
    'Playa-Vista_Los-Angeles_CA',
    'Santa-Monica_CA',
    'Sawtelle_Los-Angeles_CA',
    'Sherman-Oaks_Los-Angeles_CA',
    'Studio-City_Los-Angeles_CA',
    'Venice_CA',
    'West-Los-Angeles_CA',
    'Westwood_Los-Angeles_CA'
]
# %%
for n in neighborhoods:
    results = zipcode_scrapping(n)
    # Saving the results to a pickle file for further analysis.
    save_data(results, f'{n}_results.pkl')

# %% [markdown]
# <div style="border: 1px solid black; border-radius: 5px; overflow: hidden;">
#     <div style="background-color: black; color: white; padding: 5px; text-align: left;">
#        c.) 
#     </div>
#     <div style="padding: 10px;">
#         Write a short paragraph about the businesses or research that would use the data you scraped. Describe it's value and what it can be used for.
# </div>
