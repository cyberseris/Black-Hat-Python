import contextlib
import os
import queue
import sys
import threading
import time
import requests

# 設定不想掃描的文件擴展名列表
FILTERED = [".jpg", ".gif", ".png", ".css"]
# 設置遠程目標的網址
TARGET = "http://192.168.56.101/wordpress"
THREADS = 10

answers = queue.Queue()
# 儲存準備掃描的路徑
web_paths = queue.Queue()

def gather_paths():
    # 掃描本地 Web 應用安裝目錄裡的所有文件和目錄
    for root, _, files in os.walk('.'):
        for fname in files:
            # ".jpg", ".gif", ".png", ".css"
            if os.path.splitext(fname)[1] in FILTERED:
                continue
            # ./ + test
            path = os.path.join(root, fname)
            # ./test => /test
            if path.startswith('.'):
                path = path[1:]
            print(path)
            web_paths.put(path)

def chdir(path):
    this_dir = os.getcwd()
    os.chdir(path)
    try:
        # 將控制權轉移給 gather_paths()
        yield
    finally:
        # 回到原本的目錄
        os.chdir(this_dir)

def test_remote():
    # 檢查路徑是否可以訪問
    while not web_paths.empty():
        path = web_paths.get()
        url = f"{TARGET}{path}"
        time.sleep(2)
        r = requests.get(url)
        if r.status_code == 200:
            answers.put(url)
            sys.stdout.write("+")
        else:
            sys.stdout.write("x")
        sys.stdout.flush()

def run():
    mythreads = list()
    for i in range(THREADS):
        print(f"Spawning thread {i}")
        t = threading.Thread(target=test_remote)
        mythreads.append(t)
        t.start()
    # thread.join(): 第一個 t.start() 會先暫停等第二個 t.start() 加入，
    #                第二個 t.start() 會先暫停等第三個 t.start() 加入，
    #                直到最後一個加入後，大家一起行動，執行 test_remote
    for thread in mythreads:
        thread.join()

if __name__ == '__main__':
    with chdir("./wordpress"):
        gather_paths()
    input('Press return to continue.')
    run()
    with open('./myanswers.txt','w') as f:
        # answers = queue.Queue()
        while not answers.empty():
            f.write(f"{answers.get()}\n")
    print("done")
