import os.path
import shutil
import subprocess
import sys

import win32event
import win32service
import win32serviceutil
import servicemanager

SRCDIR = 'C:\\Users\\seris\\work'
TGTDIR = 'C:\\Windows\\TEMP'

class BHServerSvc(win32serviceutil, ServiceFramework):
    _svc_name_ = "BlackHatService"
    _svc_display_name_ = "Black Hat Service"
    _svc_decription_ = "Execute VBScripts at regular intervals. What would possibly go wrong"

def __init__(self, args):
    # 設定腳本運行的位置
    self.vbs = os.path.join(TGTDIR, 'bhservice_task.vbs')
    # 設定 1 分鐘的超時時間
    self.timeout = 1000*60
    # 初始化服務對象，確保他能夠正確地回應 SCM 的請求和其他生命週期是件
    win32serviceutil.ServiceFramework.__init__(self, args)
    # self.hWaitStop 被賦值為一個事件對象，用於通報服務何時應該停止。
    # 當事件對象被設置為有信號時，服務線程知道應該停止執行
    self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
    
def SvcStop(self):
    # 設定服務狀態
    self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
    # 停止該服務
    win32event.SetEvent(self.hWaitStop)

def SvcDoRun(self):
    # 啟動服務
    self.ReportServiceStatus(win32service.SERVICE_RUNNING)
    # 調用服務要運行的 main 函數
    self.main()

def main(self):
    # 開啟一個循環，每分鐘運行一次
    while True:
        # self.hWaitStop 被賦值為一個事件對象，用於通報服務何時應該停止。
        ret_code = win32event.WaitForSingleObject(self.hWaitStop, self.timeout)
        # 當收到停止訊號時，停止服務
        if ret_code == win32event.WAIT_OBJECT_0:
            servicemanager.LogInfoMsg("Service is stopping")
            break
        src = os.path.join(SRCDIR, 'bhservice_task.vbs')
        # 將腳本複製到目標目錄
        shutil.copy(src, self.vbs)
        # 移除 self.vbs
        os.unlink(self.vbs)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()    # 初始化
        servicemanager.PrepareToHostSingle(BHServerSvc)   # 準備託管 BHServerSvc 給 SCM
        servicemanager.StartServiceCtrlDispatcher()  # 管理 service 和 SCM 之間的通訊
    else:
        win32serviceutil.HandleCommandLine(BHServerSvc) # 安裝、移除、或是其他操作


'''
在 servicemanager.PrepareToHostSingle(BHServerSvc) 中，"託管的意思是服務管理器來託管(host)特定類別"，
但不直接涉及監聽。
在 Windows 中，"託管" 服務意味著告知服務控制管理器(SCM)有關服務的訊息，以便 SCM 可以管理服務的生命週期、
狀態、和其他操作，比如啟動、停止、暫停和繼續操作。

(Service Control Manager, SCM) 是 Windows 操作系統中的服務控制管理器，負責管理和控制系統上運行的服務。
   SCM 的主要職責包括：
1. 服務的啟動和停止： SCM 負責啟動和停止在系統上註冊的服務。它可以回應用戶或作業系統的請求，啟動
   服務來提供功能，並在需要時停止服務。
2. 服務狀態管理： SCM 跟蹤並報告服務的當前狀態，例如運行中、已暫停、已停止等。這允許用戶和系統監控服務的狀
   態，並採取適當的操作。
3. 服務請求處理：用戶或作業系統可以向 SCM 發送服務控制請求，如啟動、停止、暫停、繼續等。SCM 將這些請求傳遞給
   相應的服務。
4. 服務配置： SCM 管理服務的配置訊息，包括服務的啟動類型(自動、手動、禁用)、依賴關係等。

'''

'''
win32event.CreateEvent(lpEventAttributes, bManualReset, bInitialState, lpName)
lpEventAttributes: 指定事件對象的安全屬性，設置為 None ，表示為默認的安全屬性。
bManualReset: True: 手動 reset, False: 自動 reset
bInitialState: True: 初始狀態有信號， False: 初始狀態無信號
lpName: 指定是件對象的名稱，None: 表示創建一個無名事件
'''

'''
通常用於 win32event.WaitForSingleObject 或 win32event.WaitForMultipleObjects
win32event.WAIT_OBJECT_0: 停止訊號
win32event.WAIT_ABANDONED_0: 等待的互斥體對象已被放棄
win32event.WAIT_TIMEOUT:  等待超時
win32event.WAIT_FAILED: 等待操作失敗
'''