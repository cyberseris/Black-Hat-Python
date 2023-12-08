import requests
from bs4 import BeautifulSoup as bs

url = "https://bin.com"
r = requests.get(url)
tree = bs(r.text, 'html/parser')
for link in tree.find_all('a'):
    print(f"{link.get('href')} -> {link.text}")