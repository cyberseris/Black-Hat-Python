import os
import tempfile
import threading
import win32con
import win32file

FILE_CREATED = 1
FILE_DELETED = 2
FILE_MODIFIED = 3
FILE_RENAMED_FROM = 4
FILE_RENAMED_TO = 5

FILE_LIST_DIRECTORY = 0x0001

# 設定要監控的文件夾
PATHS = ['c:\\Windoes\\Temp', tempfile.gettempdir()]

def monitor(path_to_watch):
    # 創建 handle 來監視一個目錄的變化
    h_directory = win32file.CreateFile (
        path_to_watch,   # 要監視的目錄路徑
        FILE_LIST_DIRECTORY,    # 訪問權限，表示獲取目錄的文件列表
        # 共享模式，其他 process 可以讀、寫、刪除此文件
        win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
        None,       # 默認安全屬性
        win32con.OPEN_EXISTING,     # 打開已存在的文件或目錄 
        win32con.FILE_FLAG_BACKUP_SEMANTICS,    # 操作目錄而非文件
        None    
    )

    while True:
        try:
            # 在目錄變動時，提供通知
            results = win32file.ReadDirectoryChangesW(
                h_directory,    
                1024,   # 緩衝區大小
                True,   # 是否監視子目錄。如果設置為 True: 則表示監視目錄及其所有子目錄的變化 
                win32con.FILENOTIFY_CHANGE_ATTRIBUTES |
                win32con.FILENOTIFY_CHANGE_DIR_NAME |
                win32con.FILENOTIFY_CHANGE_FILE_NAME |
                win32con.FILENOTIFY_CHANGE_LAST_WRITE |
                win32con.FILENOTIFY_CHANGE_SECURITY |
                win32con.FILENOTIFY_CHANGE_SIZE,
                None,   # None: 使用同步模式，即阻塞等待事件的發生
                None    # 用於接收有關變化的通知，None: 同步模式, OVERLAPPED: 異步模式 
            )

            # 監控所有文件，並輸出被修改的文件名或改動的具體類型
            for action, file_name in results:
                full_filename = os.path.join(path_to_watch, file_name)
                if action == FILE_CREATED:
                    print(f'[+] Created {full_filename}')
                elif action == FILE_DELETED:
                    print(f'[-] Deleted {full_filename}')
                elif action == FILE_MODIFIED:
                    print(f'[*] Modified {full_filename}')
                    try:
                        # 讀取文件內容
                        with open(full_filename) as f:
                            contents = f.read()
                        print('[vvv] Dumping contents...')
                        print(contents)
                        print('[^^^] Dump complete.')
                    except Exception as e:
                        print(f'[!!!] Dump failed. {e}')
                elif action == FILE_RENAMED_FROM:
                    print(f'[>] Renamed from {full_filename}')
                elif action == FILE_RENAMED_TO:
                    print(f'[<] Renamed to {full_filename}')
                else:
                    print(f'[?] Unknown action on {full_filename}')
        except KeyboardInterrupt:
            break
        except Exception:
            pass

if __name__ == '__main__':
    for path in PATHS:
        monitor_thread = threading.Thread(target=monitor, args=(path,))
        monitor_thread.start()

