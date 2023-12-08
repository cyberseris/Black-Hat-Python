import requests
url = "http://boodelyboo.com"
response = requests.get(url)
print(response.text)

data = {'user': 'tim', 'password': '31337'}
response = requests.post(url, data=data)
print(response.text)