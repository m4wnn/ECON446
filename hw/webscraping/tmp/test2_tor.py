# %%
import re
import time
from bs4 import BeautifulSoup
from multiprocessing import Pool

import tbselenium.common as cm
from tbselenium.utils import launch_tbb_tor_with_stem
from tbselenium.tbdriver import TorBrowserDriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
# %%
def zipcode_scrapping(zipcode, minutes_to_sleep=2):
    # SOCK and Control ports that Tor is using.
    socks_port = 9150 
    control_port = 9151
    # Directory where the Tor Browser (Firefox) is located.
    tor_path = '/home/m4wnn/tor-browser-linux-x86_64-13.0.14/tor-browser'
    
    tor_process = launch_tbb_tor_with_stem(tbb_path=tor_path)
    
# Create a new instance of the Tor Browser.
    #driver = TorBrowserDriver(
        #tbb_path=tor_path,
        #tor_cfg=0,
        #socks_port=socks_port,
        #control_port=control_port,
    #)
    time.sleep(30)
    driver = TorBrowserDriver(tor_path, tor_cfg=cm.USE_STEM)
    driver.get(f'https://www.realtor.com/realestateandhomes-search/{zipcode}')
    time.sleep(minutes_to_sleep * 60)

    regex_property = re.compile(r'placeholder_property_\d*')
    
    property_info = []

    try:
        while True:
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
            time.sleep(minutes_to_sleep * 60)

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
                
                property_info.extend(properties)

            except NoSuchElementException:
                print("Property section not found. Continuing to next page.")
                pass  # Continue the loop, attempt to click 'Next'

            # Navigate to the next page. If the next button is not found, exit the loop.
            try:
                next_button = driver.find_element(By.LINK_TEXT, "Next")
                next_button.click()
                time.sleep(minutes_to_sleep * 60)
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
zipcode_scrapping(90001)
# %%
zipcodes = [90001]
with Pool() as pool:
    results = pool.map(zipcode_scrapping, zipcodes)
    #pool.close()
    #pool.join()
# %%
print(results)
# %%
