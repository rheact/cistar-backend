from typing import List
from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
import re

from models.rheact_state import Chemical
from helpers.errors import ScraperError

# sometimes the name of a compound cameo finds is different than the name the user inputs
# so this data structure will hold
# cas_id : name pairs so we can look up the proper name later and replace it.
cameo_names = {}

def __get_driver():
    # These options will speed up futher: 
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--no-sandbox") # linux only
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def __search_by_cmpd(cmpd_name, driver):
    #Find the 'Name (not case sensitive)' using Compound name 
    cmpd_name_input = driver.find_element_by_xpath('/html/body/div[2]/div[1]/form[1]/input[1]')

    #Send compound name keys to the compound name field 
    cmpd_name_input.send_keys(cmpd_name)

    #find the 'search Name' and click it 
    search_cmpd_btn = driver.find_element_by_xpath('/html/body/div[2]/div[1]/form[1]/input[2]')
    search_cmpd_btn.click()

def __search_by_casid(cas_id, driver):
    #Find the 'CAS NUMBER dialog box by xpath'
    cas_number_input = driver.find_element_by_xpath('/html/body/div[2]/div[1]/form[2]/input[1]')
    
    #Enter cas-id in the 'CAS NUMBER dialog'
    cas_number_input.send_keys(cas_id)
    
    #find the 'CAS Number (with or without dashes)' button and click it 
    search_cas_btn = driver.find_element_by_xpath('/html/body/div[2]/div[1]/form[2]/input[2]')
    search_cas_btn.click()

def __new_search_button(driver):
    new_search_btn = driver.find_element_by_xpath('/html/body/div[1]/a[3]')
    new_search_btn.click()

def __add_chemical(cas_id, driver):
    # add the cas_id : name pair to names data structure
    name = add_to_chemical_btn = driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[2]/a')
    cameo_names[cas_id] = name.text

    #This is by default the first entry in the search
    add_to_chemical_btn = driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[2]/p/a[2]')
    add_to_chemical_btn.click()

#To search for a string in the page source 
def find_txt(string_to_find, src):
    return re.search(r'{}'.format(string_to_find), src)

def get_cameo(compounds: List[Chemical]):
    driver = __get_driver()
    try:
        driver.get('https://cameochemicals.noaa.gov/search/simple')
    except:
        raise ScraperError('Unable to access the CAMEO website, please visit cameochemicals.noaa.gov for chemical compatibility analysis')

    # will want to return html element and errors, if any
    html_element = ''
    details_html = ''
    errors = []

    for cmpd in compounds: 
        cmpd_name = cmpd.productName
        cas_id = cmpd.casNo
        
        __search_by_cmpd(cmpd_name, driver)
        if find_txt('No matches were found', driver.page_source):

            __new_search_button(driver)
            __search_by_casid(cas_id, driver)
            
            # Check if CAS-ID parsed is proper or not 
            try: 
                print('CAS-ID {} for compound {} is invalid, skipping'.format(cas_id, cmpd_name))
                driver.find_element_by_xpath('/html/body/div[2]/div[1]/form[2]/span')
                __new_search_button(driver)
                continue 
            except: 
                # Check if CAS-ID is found in the dataset 
                if find_txt('No matches were found', driver.page_source):
                    #Print this out in the dialog box 
                    print('{} with CAS-ID: {} not found in the Cameo dataset'.format(cmpd_name, cas_id))
                    __new_search_button(driver)
                else:
                    print('Match found for {} with CAS-ID: {}, added to the data using CAS-ID'.format(cmpd_name, cas_id))
                    __add_chemical(cas_id, driver)

        elif find_txt(cas_id, driver.page_source):
            __add_chemical(cas_id, driver)
        else:
            print('partial match found for {}, not added to the data'.format(cmpd_name))
            errors.append('partial match found for {}, not added to the data'.format(cmpd_name))

        __new_search_button(driver)

    try:
        predict_react_btn = driver.find_element_by_xpath('/html/body/div[1]/a[7]')
        predict_react_btn.click()
        
        react_table = driver.find_element_by_xpath('/html/body/div[2]/table')

        #This is the html element for the table -- printing this out will give all the code 
        html_element = react_table.get_attribute('outerHTML')

        details_arr = driver.find_elements_by_xpath('//*[preceding-sibling::table[@id="compat_chart"] and following-sibling::div[@class="footer"]]')
        details_html_arr = []
        for d in details_arr:
            details_html_arr.append(d.get_attribute('outerHTML'))

        details_html = ''.join(details_html_arr)
        details_html = re.sub(' href=".*"', '', details_html)
        details_html = re.sub(
            '(<table width="100%" summary="for page layout only">|<tbody><tr>|<td align="left"><a>Documentation</a></td>|<td align="right"><a>Back to Chart</a></td>|</tr>|</tbody></table>|<br>)',
            '', 
            details_html
        )
        details_html = re.sub('h2', 'h3', details_html)
        details_html = re.sub('(<a>|<em>)', '<span>', details_html)
        details_html = re.sub('</a>|</em>', '</span>', details_html)
    except: 
        print('Exception No compatiblity matrix formed')
        errors.append('No compatiblity matrix formed')
        html_element = ''
        details_html = ''

    # replace the cameo names with the ones the user uploaded
    for compound in compounds:
        try:
            details_html = details_html.replace(cameo_names[compound.casNo], compound.productName)
            html_element = html_element.replace(cameo_names[compound['casNo']], compound['productName'])
        except:
            pass

    driver.close()

    return {
        'html_element': html_element,
        'details_html': details_html,
        'errors': errors,
    }
