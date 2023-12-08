import ipaddress
import os
import socket
import struct
import sys
import threading
import time

SUBNET = "172.28.0.0/16"

# 定義簽名，用於確認收到 ICMP response 是由發送的 UDP 封包所觸發的
MESSAGE = 'PYTHONRULES' 

class IP:
    def __init__(self, buff=None):
        header = struct.unpack('<BBHHHBBH4s4s', buff)

        # 版本 ex:0100, 4 
        self.ver = header[0] >> 4
        # 表頭長度 ex: 0101, header len: 20 bytes 
        self.ihl = header[0] & 0xF
        # 服務類型 ex: 0x00 
        self.tos = header[1]
        # 總長度 ex: 40
        self.len = header[2] 
        # 標識 ex: 0x212:
        self.id = header[3]
        # offset ex: 0
        self.offset = header[4]
        # 生存時間 ex: 128
        self.ttl = header[5] 
        # 協議 ex: TCP
        self.protocol_num = header[6] 
        # header 校驗和 ex: 0x0000
        self.sum = header[7]
        # 來源 ip 地址
        self.src = header[8]
        # 目的 IP 地址
        self.dst = header[9]

        # 轉換成 IP 地址的可讀形式
        self.src_address = ipaddress.ip_address(self.src)
        self.dst_address = ipaddress.ip_address(self.dst)

        self.protocol_map = {1: "ICMP", 6: "TCP", 17: "UDP"}

        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except Exception as e:
            print("%s No protocol for %s" % (e, self.protocol_num))
            self.protocol = str(self.protocol_num)

class ICMP:
    def __init__(self, buff):
        header = struct.unpack('<BBHHH', buff)
        # 類型
        self.type = header[0]
        # 代碼
        self.code = header[1]    
        # 表頭校驗和
        self.sum = header[2]
        # 標識
        self.id = header[3]
        # 請求
        self.seq = header[4]

def udp_sender():
    # 這段 code 執行後就會關閉
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sender:
        # SUBNET:  within the specified IP network (SUBNET)
        # ipaddress 用來產生 hosts
        for ip in ipaddress.ip_network(SUBNET).hosts():
            # 傳送 UDP message 給所有 host, 
            # bytes(MESSAGE, 'utf8'): 使用 utf-8 encoding 將 message 轉換為 bytes 物件
            # port: 65212
            sender.sendto(bytes(MESSAGE, 'utf8'), (str(ip), 65212))

class Scanner:
    def __init__(self, host):
        self.host = host
        if os.name == "nt":
            socket_protocol = socket.IPPROTO_IP
        else:
            socket_protocol = socket.IPPROTO_ICMP

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
        self.socket.bind((host,0))

        # 設置 socket, 抓取包含 IP header 的封包
        self.socket.setsocketopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

        if os.name == "nt":
            # 如果是 Windows，執行時啟用混雜模式
            self.socket.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

    def sniff(self):
        hosts_up = {f"{str(self.host)} *"}
        try:
            while True:
                # 讀取一個封包
                raw_buffer = self.socket.recvfrom(65535)[0]
                # 將前 20 字節轉換成 IP header 對象
                ip_header = IP(raw_buffer[0:20])
                if ip_header.protocol == "ICMP":
                    # 計算 ICMP 資料在原始
                    offset = ip_header.ihl * 4
                    buf = raw_buffer[offset:offset + 8]

                    # 按照 ICMP 結構進行解析
                    icmp_header = ICMP(buf)
                    # 判斷目標不可達，port 不可達
                    if icmp_header.code == 3 and icmp_header.type == 3:
                        # 檢查這個 response 是否來自我們正在掃描得子網段
                        if ipaddress.ip_address(ip_header.src_address) in ipaddress.IPv4Network(SUBNET):
                            if raw_buffer[len(raw_buffer) - len(MESSAGE):] == bytes(MESSAGE, 'utf8'):
                                tgt = str(ip_header.src_address)
                                if tgt != self.host and tgt not in hosts_up:
                                    hosts_up.add(str(ip_header.src_address))
                                    print(f"Host Up: {tgt}")

        except KeyboardInterrupt:
            if os.name == "nt":
                # 關閉網路卡的混雜模式
                self.socket.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)

            print('\nUser interrupted.')
            if hosts_up:
                print(f"\n\nSummary: Hosts up on {SUBNET}")
            for host in sorted(hosts_up):
                print(f"{host}")
            print("")
            sys.exit()

if __name__ == '__main__':
    if len(sys.argvv) == 2:
        host = sys.argv[1]
    else:
        host = "172.28.216.90"
    
    s = Scanner(host)
    time.sleep(5)
    # 先為 udp_sender 開啟一個獨立的線程，以免干擾 sniffer 的效果
    t = threading.Thread(target = udp_sender)
    t.start()
    s.sniff()
