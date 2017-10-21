from bs4 import BeautifulSoup
import re
import requests

response = requests.get('https://arcticeider.com/en/about')
soup = BeautifulSoup(response.content, 'html.parser')

print(soup.find('a', href=re.compile('facebook')).get('href'))
