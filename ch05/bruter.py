import queue
import sys
import threading
import requests.exceptions

AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:19.0) Gecko/20100101 Firefox/19.0"
EXTENSIONS = ['.php','.bak', '.orig', '.inc']
TARGET = "http://testphp.vulnweb.com"
THREAD = 50
WORDLIST = "./svn_digger/all.txt"

# 因為檔案內容為 resume: ex:root, Entries, lang, home.php, setup.php, 所以要變成 /Entries, /Lang/, /setup.php 
def get_words(resume=None):
    def extend_words(word):
        # setup.php
        if "." in word:
            words.put(f"/{word}")
        else:
            # /Lang/
            words.put(f"/{word}/")
        # /Lang.php
        for extension in EXTENSIONS:
            words.put(f"/{word}{extension}")  
    
    with open(WORDLIST) as f:
        raw_words = f.read()

    found_resume = False
    words = queue.Queue()

    for word in raw_words.split():
        # 設置成上一次掃描到的最後路徑
        if resume is not None:
            if found_resume:
                extend_words(word)
            elif word == resume:
                found_resume = True
                print(f"Resuming wordlist from: {resume}")
        else:
            print(word)
            extend_words(word)
        resume = word
    # 改造完所有的 word，得到待掃描的路徑 /Entries, /Lang/, /setup.php 
    return words

    def dir_bruter(words):
        headers = {'User-Agent': AGENT}
        while not words.empty():
            # 生成遠程目標的 URL
            url = f"{TARGET}{words.get()}"
            try:
                r = requests.get(url, headers=headers)
            except requests.exceptions.ConnectionError:
                sys.stderr.write("x")
                sys.stderr.flush()
                continue
            
            if r.status_code == 200:
                print(f"\nSuccess ({r.status_code}: {url})")
            elif r.status_code == 404:
                sys.stderr.write(".")
                sys.stderr.flush()
            else:
                print(f"{r.status_code} => {url}")
                                                                                      
if __name__ == '__main__':
    words = get_words()
    print("Press return to continue.")
    sys.stdin.readline()
    for _ in range(THREAD):
        t = threading.Thread(target=dir_bruter, args=(words,))
        t.start()