#!/usr/bin/env python3

#
# Grabs weather data from a local weather station and extracts the current temperature and weather.
#
# 03Jun18 Mayer Feldman
#

import requests
import re
from bs4 import BeautifulSoup

#Get the html via requests module
page = requests.get('https://www.timeanddate.com/weather/usa/santa-barbara')

#parse the html file using Beautiful Soup
soup = BeautifulSoup(page.text, 'html.parser')
#print(soup.prettify())
#To find the temp, I found the class it's located in. Below finds the temp via the tag 'h2' and changes
#it to a string using the .text extension.
findTemp = soup.find(class_ = 'h2').text
findOvercast = soup.find('p').text
print(findOvercast)
print(findTemp)

