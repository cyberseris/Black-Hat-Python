import requests
from lxml import etree
from io import BytesIO

url = "https://nostarch.com"
r = requests.get(url)
content = r.content

parser = etree.HTMLParser()
content = etree.parse(BytesIO(content), parser=parser)

for link in content.findall("a"):
    print(f"{link.get('href')} -> {link.text}")