import wmi

def log_to_file(message):
    with open('process_monitor_log.csv', 'a') as fd:
        fd.write(f'{message}\r\n')

def monitor():
    log_to_file('CommandLine, Time, Executable, Parent PID, PID, User, Privileges')
    # 創建 WMI 實例
    c = wmi.WMI()
    # 監控 process 創建事件
    process_watcher = c.Win32_Process.watch_for('creation')

    while True:
        try:
            # 循環等待返回一個新的 process 事件
            new_process = process_watcher()
            # 獲取 process 的全部訊息
            cmdline = new_process.CommandLine
            create_data = new_process.CreationDate
            executable = new_process.ExecutablePath
            parent_pid = new_process.ParentProcessId
            pid = new_process.ProcessId
            proc_owner = new_process.GetOwner()

            privileges = 'N/A'
            process_log_message = (
                f'{cmdline}, {create_date}, {executable},'
                f'{parent_pid}, {pid}, {proc_owner}, {privileges}'
            )
            print(process_log_message)
            print()

            # 紀錄到日誌文件中
            log_to_file(process_log_message)
        except Exception:
            pass

if __name__ == '__main__':
    monitor()