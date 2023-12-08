import argparse
import shlex
import socket
import subprocess
import sys
import textwrap
import threading


def execute(cmd):
    cmd = cmd.strip()
    if not cmd:
        return
    
    # 創建一個帶命令列介面的程式
    output = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT)
    return  output.decode()

class NetCat:
    def __init__(self, args, buffer=None):
        self.args = args
        self.buffer = buffer
        # 創建 socket 對象
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # S.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1) 這裡 value 設定為 1，表示將 SO_REUSEADDR 標記為 TRUE，作業系統會在伺服器 socket 被關閉或伺服器進程終止後馬上釋放該伺服器的連接埠，否則作業系統 會保留幾分鐘該連接埠。
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def run(self):
        if self.args.listen:
            # 如果是接收方，啟動監聽
            self.listen()
        else:
            # 如果是發送方，執行發送
            self.send()

    def send(self):
        # 連接伺服器
        self.socket.connect((self.args.target, self.args.port))
        if self.buffer:
            self.socket.send(self.buffer)

        try:
            # 處理 response
            while True:
                recv_len = 1
                response = ''
                while recv_len:
                    data = self.socket.recv(4096)
                    recv_len = len(data)
                    response += data.decode()
                    if recv_len < 4096:
                        break
                    if response:
                        print(response)
                        buffer = input('>')
                        buffer += '\n'
                        # 等待用戶輸入新的內容，再把新的內容發給 target
                        self.socket.send(buffer.encode())
        except KeyboardInterrupt:
            # 使用 Ctrl C 手動關閉連接
            print('User terminated.')
            self.socket.close()
            sys.exit()

    def listen(self):
        # 監聽綁定
        self.socket.bind((self.args.target, self.args.port))
        # 啟動監聽，最多 5 個線程
        self.socket.listen(5)
        while True:
            client_socket, _ = self.socket.accept()
            client_thread = threading.Thread(target=self.handle, args=(client_socket,))
            client_thread.start()

    # 伺服器端
    def handle(self, client_socket):
        # operation 參數
        # execute operation
        if self.args.execute:
            # 執行命令
            output = execute(self.args.execute)
            client_socket.send(output.encode())
        # upload operation
        elif self.args.upload:
            # mytest.txt 文件上傳
            file_buffer = b''
            while True:
                # 接收上傳資料
                data = client_socket.recv(4096)
                if data:
                    file_buffer += data
                else:
                    break
            # 檔名： self.args.upload，將檔案存到伺服器端
            with open(self.args.upload, 'wb') as f:
                f.write(file_buffer)
            message = f'Saved file {self.args.upload}'
            client_socket.send(message.encode())
        elif self.args.command:
            # 打開一個 shell
            cmd_buffer = b''
            # cmd: cat /etc/passwd
            while True:
                try:
                    client_socket.send(b"TEST: #>")
                    while '\n' not in cmd_buffer.decode():
                        cmd_buffer += client_socket.recv(64)
                    response = execute(cmd_buffer.decode())
                    if response:
                        client_socket.send(response.encode())
                    cmd_buffer = b''
                except Exception as e:
                    print(f'server killed {e}')
                    self.socket.close()
                    sys.exit()


if __name__ == '__main__':
    #命令幫助訊息
    parser = argparse.ArgumentParser(
    description = 'Netcat Tool',
    formatter_class = argparse.RawDescriptionHelpFormatter,
    epilog = textwrap.dedent('''Example: 
    netcat.py -t 192.168.1.108 -p 5555 -l -c #command shell
    netcat.py -t 192.168.1.108 -p 5555 -l -u=mytest.txt # upload file
    netcat.py -t 192.168.1.108 -p 5555 -l -e=\" cat /etc/passwd\" #execute command
    echo 'XYZ' | ./netcat.py -t 192.168.1.108 -p 135 #echo text to server port 135
    netcat.py -t 192.168.1.108 -p 5555 # 連接伺服器                         
    ''')
    )

# 命令參數
parser.add_argument('-c', '--command', action='store_true', help='command shell')
parser.add_argument('-e', '--execute', help='execute specified command')
parser.add_argument('-l', '--listen', action='store_true', help='listen')
parser.add_argument('-p', '--port', type=int, default='192.168.1.203', help='specified IP')
parser.add_argument('-t', '--target', default='192.168.1.203', help='specified IP')
parser.add_argument('-u', '--upload', help='upload file')
args = parser.parse_args()

# 程式監聽，在緩衝區填上空白資料
if args.listen:
    buffer = ''
else:
    buffer = sys.stdin.read()

nc = NetCat(args, buffer.encode())
nc.run()













