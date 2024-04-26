# %%
import sys
import re
import time
import random
import numpy as np
import os

from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

from stem import Signal
from stem.control import Controller

import tbselenium.common as cm
from tbselenium.utils import launch_tbb_tor_with_stem
from tbselenium.tbdriver import TorBrowserDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from multiprocessing import Pool
from tqdm import tqdm
import pickle as pkl
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
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <zipcode>")
        sys.exit(1)
    
    zipcode = sys.argv[1]  # Obtener el zipcode desde la línea de comandos
    print(f"Scraping properties for zipcode: {zipcode}")
    results = zipcode_scrapping(zipcode)
    print(f'Properties found: {len(results)}')

    save_data(results, f'{zipcode}_results.pkl')
