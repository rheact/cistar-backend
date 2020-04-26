from selenium import webdriver 
from time import time, sleep
from PIL import Image
from io import BytesIO
import csv
from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
chrome_options = Options()
#These options will speed up the futher: 
#chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")

#chrome_options.add_argument("--no-sandbox") # linux only
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)

#Tert-Butyl Alchol - '75-65-0'
#Acetic Acid -- '64-19-7'
#ETHYL ORTHOFORMATE -- '122-51-0'

#Running headless instance of Chrome 
cas_no = ['75-65-0','64-19-7','122-51-0'] 
driver.get('https://cameochemicals.noaa.gov/search/simple')

for cmpd in cas_no: 
	cas_number_input = driver.find_element_by_xpath('/html/body/div[2]/div[1]/form[2]/input[1]')
	cas_number_input.send_keys(cmpd)

	search_cas_btn = driver.find_element_by_xpath('/html/body/div[2]/div[1]/form[2]/input[2]')
	search_cas_btn.click()
	print(driver.current_url)
	#This is by default the first entry in the search
	add_to_chemical_btn = driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[2]/p/a[2]')
	add_to_chemical_btn.click()
	sleep(2)

	new_search_btn = driver.find_element_by_xpath('/html/body/div[1]/a[3]')
	new_search_btn.click()

predict_react_btn = driver.find_element_by_xpath('/html/body/div[1]/a[7]')
predict_react_btn.click()

#import table 
react_table = driver.find_element_by_xpath('/html/body/div[2]/table')

#This is the html element for the table -- printing this out will give all the code 
html_element = react_table.get_attribute('outerHTML')
#Convert to csv: 
#with open('react_table.csv', 'w', newline='') as csvfile:
#    wr = csv.writer(csvfile)
#    for row in react_table.find_elements_by_css_selector('tr'):
#        wr.writerow([d.text for d in row.find_elements_by_css_selector('td')])

#Taking screenshot 
location = react_table.location
size = react_table.size

png = driver.get_screenshot_as_png()
im = Image.open(BytesIO(png))

left = location['x']
top = location['y']
right = location['x'] + size['width']
bottom = location['y'] + size['height']
im = im.crop((left, top, right, bottom))
im.save('screenshot.png')
driver.close()