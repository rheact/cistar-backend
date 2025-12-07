from typing import List
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import os

from models.rheact_state import Chemical
from helpers.errors import ScraperError

cameo_names = {}

# ------------------------- Driver Setup -------------------------
def __get_driver():
    # These options will speed up futher: 
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")          # recommended for modern Chrome
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")            # required on Linux
    chrome_options.add_argument("--disable-dev-shm-usage") # required on Heroku
    chrome_options.add_argument("--disable-extensions") 
    driver = webdriver.Chrome(options=chrome_options)
    return driver

# ------------------------- Helper Functions -------------------------
def wait_and_click(driver, xpath, timeout=3):
    element = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.XPATH, xpath))
    )
    element.click()
    return element

def wait_and_send_keys(driver, xpath, text, timeout=3):
    element = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )
    element.clear()
    element.send_keys(text)
    return element

def find_txt(string_to_find, src):
    return re.search(r'{}'.format(string_to_find), src)

# ------------------------- CAMEO Search Functions -------------------------
def __search_by_cmpd(cmpd_name, driver):
    wait_and_send_keys(driver, '/html/body/div[2]/div[1]/form[1]/input[1]', cmpd_name)
    wait_and_click(driver, '/html/body/div[2]/div[1]/form[1]/input[2]')

def __search_by_casid(cas_id, driver):
    wait_and_send_keys(driver, '/html/body/div[2]/div[1]/form[2]/input[1]', cas_id)
    wait_and_click(driver, '/html/body/div[2]/div[1]/form[2]/input[2]')

def __new_search_button(driver):
    wait_and_click(driver, '/html/body/div[1]/a[3]')

def __add_chemical(cas_id, driver):
    try:
        name_elem = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[2]/div[2]/a'))
        )
        cameo_names[cas_id] = name_elem.text

        add_btn = driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/div[2]/p/a[2]')
        add_btn.click()
    except:
        print(f"Failed to add chemical {cas_id}")

# ------------------------- Main get_cameo Function -------------------------
def get_cameo(compounds: List[Chemical]):
    driver = __get_driver()
    try:
        driver.get('https://cameochemicals.noaa.gov/search/simple')
    except:
        driver.quit()
        raise ScraperError('Unable to access the CAMEO website')

    html_element = ''
    details_html = ''
    errors = []

    for cmpd in compounds:
        cmpd_name = cmpd.productName
        cas_id = cmpd.casNo

        try:
            __search_by_cmpd(cmpd_name, driver)
            if find_txt('No matches were found', driver.page_source):
                __new_search_button(driver)
                __search_by_casid(cas_id, driver)

                if find_txt('No matches were found', driver.page_source):
                    print(f'{cmpd_name} with CAS-ID {cas_id} not found in the Cameo dataset')
                    __new_search_button(driver)
                    errors.append(f'{cmpd_name} with CAS-ID {cas_id} not found')
                else:
                    print(f'Match found for {cmpd_name} with CAS-ID {cas_id}, adding')
                    __add_chemical(cas_id, driver)
            elif find_txt(cas_id, driver.page_source):
                __add_chemical(cas_id, driver)
            else:
                print(f'Partial match found for {cmpd_name}, not added')
                errors.append(f'Partial match found for {cmpd_name}')
        except Exception as e:
            print(f"Error processing {cmpd_name}: {e}")
            errors.append(f"Error processing {cmpd_name}: {e}")

        __new_search_button(driver)

    try:
        # Generate the compatibility chart
        wait_and_click(driver, '/html/body/div[1]/a[7]')
        react_table = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/table'))
        )
        html_element = react_table.get_attribute('outerHTML')

        details_arr = driver.find_elements(By.XPATH, '//*[preceding-sibling::table[@id="compat_chart"] and following-sibling::div[@class="footer"]]')
        details_html_arr = [d.get_attribute('outerHTML') for d in details_arr]
        details_html = ''.join(details_html_arr)

        # Cleanup HTML
        details_html = re.sub(' href=".*"', '', details_html)
        details_html = re.sub(
            '(<table width="100%" summary="for page layout only">|<tbody><tr>|<td align="left"><a>Documentation</a></td>|<td align="right"><a>Back to Chart</a></td>|</tr>|</tbody></table>|<br>)',
            '', 
            details_html
        )
        details_html = re.sub('h2', 'h3', details_html)
        details_html = re.sub('(<a>|<em>)', '<span>', details_html)
        details_html = re.sub('</a>|</em>', '</span>', details_html)

    except Exception as e:
        print(f'Exception: {e}')
        errors.append('No compatibility matrix formed')

    # Replace CAMEO names with user-provided names
    for compound in compounds:
        try:
            details_html = details_html.replace(cameo_names.get(compound.casNo, ''), compound.productName)
            html_element = html_element.replace(cameo_names.get(compound.casNo, ''), compound.productName)
        except:
            pass

    driver.quit()
    return {
        'html_element': html_element,
        'details_html': details_html,
        'errors': errors,
    }
