import win32con
import wmi
import win32api
import win32security

def get_process_privileges(pid):
    try:
        # 使用 Process ID 取得目標 Process 控制碼 handle
        hproc = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION, False, pid)
        # 打開 Process toke
        htok = win32security.OpenProcessToken(hproc, win32con.TOKEN_QUERY) 
        # 查詢該 process 的 token 訊息， win32security.TokenPrivileges: 破解處理程序權杖
        privs = win32security.GetTokenInformation(htok, win32security.TokenPrivileges)
        privileges = ''
        for priv_id, flags in privs:
            # 判斷是否啟用標識位
            if flags == win32security.SE_PRIVILEGE_ENABLED | win32security.SE_PRIVILEGE_ENABLED_BY_DEFAULT:
                # 找尋這個許可權的可讀名稱
                privileges += f'{win32security.LookupPrivilegeName(None, priv_id)}|'
    except Exception:
        privileges = 'N/A'
    return privileges  

def log_to_file(message):
    with open('process_monitor_log.csv', 'a') as fd:
            fd.write(f'{message}\r\n')

def monitor():
    log_to_file('CommandLine, Time, Executable, Parent PID, PID, User, Privileges')
    # 創建 WMI 實例
    c = wmi.WMI()
    # 監控進程創建事件
    process_watcher = c.Win32_Process.watch_for('creation')

    while True:
        try:
            # 循環等待返回一個新的進程
            new_process = process_watcher()
            # 獲取進程的全部訊息
            cmdline = new_process.CommandLine
            create_date = new_process.CreationDate
            executable = new_process.ExecutablePath
            parent_pid = new_process.ParentProcessId
            pid = new_process.ProcessId
            proc_owner = new_process.GetOwner()

            privileges = get_process_privileges(pid)
            process_log_message = (
                f'{cmdline}, {create_date}, {executable},'
                f'{parent_pid}, {pid}, {proc_owner}, {privileges}'
            )

            print(process_log_message)
            print()
            # 記錄到日誌文件中
            log_to_file(process_log_message)
        except Exception:
            pass

if __name__ == '__main__':
    monitor()