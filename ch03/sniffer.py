import os 
import socket

HOST = '172.28.216.90'

def main():
    # windows 設定為 'nt'，而 Unix-like systems (包括 Linux 和 macOS) 則設定為 'posix'
    if os.name == 'nt':
        socket_protocol = socket.IPPROTO_IP
    else:
        socket_protocol = socket.IPPROTO_ICMP

    # 構建一個 socket 對象
    sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
    # specific network interface 和 port，自動選擇可以使用的 port
    sniffer.bind((HOST, 0))

    # 設置 socket，抓取包含 IP header 封包
    sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    if os.name == 'nt':
        # 如果是 windows，執行時，啟用混雜模式
        # ioctl: 方法是用來執行 input/output control operations
        # socket.SIO_RCVALL: 封包抓取的選項，當它為 socket.RCVALL_ON 選項時，它會擷取所有封包
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

        # 讀取一個封包
    print(sniffer.recvfrom(65565))
    if os.name == 'nt':
        # 關閉網路卡的混雜模式，不接收通過網路介面的所有 IPv4 和 IPv6，因為他只要讀取一個封包就好
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)

if __name__ == '__main__':
    main()