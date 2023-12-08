import random
import time
import requests 
from win32com import client

username = "seris"
password = "sekret"
api_dev_key = "testNMyjkldfghjoRTYUIKLNMfghjktest"


def plain_paste(title, contents):
    # 創建便簽所需的憑證
    login_url = "https://pastebin.com/api/api_login.php"
    login_data = {
        'api_dev_key': api_dev_key,
        'api_user_name': username,
        'api_user_password': password
    }

    r = requests.post(login_url, data=login_data)
    api_user_key = r.text

    # 登錄到 Pastebin 帳號
    paste_url = "https://pastebin.com/api/api_post.php"
    paste_data = {
        'api_paste_name': title,
        'api_paste_code': contents.decode(),
        'api_dev_key': api_dev_key,
        'api_user_key': api_user_key,
        'api_option': 'paste',
        'api_paste_private': 0,
    }   
    r = requests.post(paste_url, data=paste_data)
    print(r.status_code)
    print(r.text)

def wait_for_browser(browser):
    # 用來等待瀏覽器完成當前操作
    while browser.ReadyState !=4 and browser.ReadyState != 'complete':
        time.sleep(0.1)

# 讓瀏覽器的行為像人一樣
def random_sleep():
    time.sleep(random.randint(5, 10))

def login(ie):
    # 讀取 DOM 中的所有元素
    full_doc = ie.Document.all
    for elem in full_doc:
        if elem.id== 'loginform-username':
            elem.setAttribute('value', username)
        elif elem.id == 'loginform-password':
            elem.setAttribute('value', password)
    
    random_sleep()
    if ie.Document.Forms[0].id == 'w0'
        ie.document.form[0].submit()
    wait_for_browser(ie)

def submit(ie, title, contents):
    # 獲取標題和正文的輸入框
    full_doc = ie.Document.all
    for elem in full_doc:
        if elem.id == 'postform-name':
            elem.setAttribute('value', title)
        elif elem.id == 'postform-text':
            elem.setAttribute('value', contents)
    
    if ie.Document.forms[0].id == 'w0':
        ie.decument.forms[0].submit()
    random_sleep()
    wait_for_browser(ie)

def ie_paste(title, contents):
    # 創建一個 IE 瀏覽器 COM 對象的實例
    ie = client.Dispatch('InternetExplorer.Application')
    # 設定 process 在螢幕上顯示
    ie.Visible = 1

    ie.Navigate('https://pastebin.com/login')
    wait_for_browser(ie) # 等它執行完
    login(ie)

    ie.Navigate('https://pastebin.com/')
    wait_for_browser(ie)
    submit(ie, title, contents.decode())

    # 關閉瀏覽器實例
    ie.Quit()

if __name__ == '__main__':
    ie_paste('title', b'contents')
    # plain_paste(title, contents)

'''
READYSTATE_UNINITIALIZED (0): The object has been created, but the open method hasn't been called yet.
READYSTATE_LOADING (1): The object is being initialized.
READYSTATE_LOADED (2): The object has been initialized.
READYSTATE_INTERACTIVE (3): The object is loading data.
READYSTATE_COMPLETE (4): The object has finished loading.
'''