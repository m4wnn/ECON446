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

from tbselenium.tbdriver import TorBrowserDriver
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException

# %%
# %%
# User agent to simulate a browser in selenium.
options = Options()
options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")

# %%
# Directory where the Tor Browser (Firefox) is located.
tor_path = '/home/m4wnn/tor-browser-linux-x86_64-13.0.14/tor-browser'
# SOCK and Control ports that Tor is using.
socks_port = 9150 
control_port = 9151
# %%
# Create a new instance of the Tor Browser.
driver = TorBrowserDriver(tor_path, socks_port=socks_port, control_port=control_port)
# %%
# Open the website in the browser.
driver.get("https://www.realtor.com/realestateandhomes-search/90024")
time.sleep(4 * 60)
# %%
# Init list to store properties info.
property_info = []
# %%
page_num = 1
while True:
    print(f'Scraping page {page_num}...')
    
    # Scroll to the bottom of the page.
    body = driver.find_element(By.TAG_NAME, 'body')
    body.send_keys(Keys.END)
    time.sleep(4 * 60)
    
    # Get the properties section.
    property_section = driver.find_element(
        By.CSS_SELECTOR,
        'section[class^="PropertiesList_propertiesContainer"]'
    )
    section_content = BeautifulSoup(
        property_section.get_attribute('innerHTML'),
        'html.parser'
    )

    # Get all the properties in the section.
    regex_property = re.compile(r'placeholder_property_\d*')

    # Extend the list of properties info. 
    property_info.extend(
        section_content.find_all(
            'div',
            id = lambda x: x and regex_property.match(x)
        )
    )
    
    # Navigate to the next page. If the next button is not found, exit the loop.
    # If an unexpected error occurs, exit the loop.
    try:
        next_button = driver.find_element(By.LINK_TEXT, "Next")
        next_button.click()
        
        page_num += 1
        time.sleep(4 * 60)
    except StaleElementReferenceException:
        print("Next button not found. Exiting loop.")
        break
    except Exception as e:
        print(f"Unexpected error: {e}")
        break
# %%
# Close the browser.
driver.quit()
# %%
