# %%
import re
import time
import random
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from stem import Signal
from stem.control import Controller

import tbselenium.common as cm
from tbselenium.utils import launch_tbb_tor_with_stem
from tbselenium.tbdriver import TorBrowserDriver

# %%
def random_sleep(minimum=2, maximum=5):
    """Generate a random sleep time to mimic human behavior."""
    time.sleep(random.uniform(minimum, maximum))

# %%
#def human_like_scroll(driver):
    #"""Simulate human-like scrolling behavior."""
    #scroll_script = "window.scrollTo(0, document.body.scrollHeight/2);"
    #driver.execute_script(scroll_script)
    #random_sleep(1, 3)
    #scroll_script = "window.scrollTo(0, document.body.scrollHeight);"
    #driver.execute_script(scroll_script)
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
        time.sleep(random.uniform(0.5, 30))  # Adjust timing as needed

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
def zipcode_scrapping(zipcode):
    tor_path = '/home/m4wnn/tor-browser-linux-x86_64-13.0.14/tor-browser'
    tor_process = launch_tbb_tor_with_stem(tbb_path=tor_path)

    # Setting a random user-agent using pref_dict
    user_agent_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko"
    ]
    random_user_agent = random.choice(user_agent_list)
    pref_dict = {"general.useragent.override": random_user_agent}

    # Create a TorBrowserDriver instance with customized user-agent
    driver = TorBrowserDriver(tor_path, tor_cfg=cm.USE_STEM, pref_dict=pref_dict)

    regex_property = re.compile(r'placeholder_property_\d*')
    property_info = []
    try:
        while True:
            switch_tor_circuit()  # Switch Tor circuit before loading the page
            driver.get(f'https://www.realtor.com/realestateandhomes-search/{zipcode}')
            random_sleep(3, 6)

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
                
                property_info.extend(properties)

            except NoSuchElementException:
                print("Property section not found. Continuing to next page.")
                pass

            try:
                next_button = driver.find_element(By.LINK_TEXT, "Next")
                next_button.click()
                random_sleep(3, 6)
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
# Run the function
results = zipcode_scrapping(90051)

# %%
