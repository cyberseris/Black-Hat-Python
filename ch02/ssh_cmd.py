import getpass
import paramiko

def ssh_command(ip, port, user, passwd, cmd):
    client = paramiko.SSHClient()
    # 允許連接到沒有 host key 的伺服器上 
    # 自動新增 hostname 和 key 到本地端 .ssh/known_hosts 檔案
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # 利用帳號密碼進行伺服器登入，若有指定 port 亦可利用 port 參數進行設定
    client.connect(ip, port=port, username=user, password=passwd)

    _, stdout, stderr = client.exec_command(cmd)
    output = stdout.redlines() + stderr.readlines()
    if output:
        print("--- Output ---")
        for line in output:
            print(line.strip())

if __name__ == '__main__':
    user = input('Username: ')
    password = getpass.getpass()
    # Password: _
    ip = input('Enter server IP: ') or '192.168.56.101'
    port = input('Enter port or <CR>: ') or 2222
    cmd = input('Enter command or <CR>: ') or 'id'
    ssh_command(ip, port, user, password, cmd)