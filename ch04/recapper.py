import collections
import os

# 設置保存圖片的目錄
import re
import sys
import zlib
from scapy.layers.inet import TCP
from scapy.utils import rdpcap

OUTPUT = "/root/Desktop/pictures"
PCAPS = "/root/Downloads" # 設定 pcap 文件路徑

# 定義 Response 命名元祖
Response = collections.namedtuple('Response', ['header', 'payload'])

def get_header(payload):
    try:
        # 提取 http header
        # payload: payload = b'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<html><body>Hello, World!</body></html>'
        # header_raw: header_raw = b'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n'
        header_raw = payload[:payload.index(b'\r\n\r\n') + 2]
    except ValueError:
        sys.stdout.write("-")
        sys.stdout.flush()
        return None

    header = dict(re.findall(r'(?P<name>.*?):(?P<value>.*?)\r\n', header_raw.decode()))
    if "Content-Type" not in header:
        return None
    return header

def extract_content(Response, content_name='image'):
    content, content_type = None, None
    if content_name in Response.header['Content-Type']:
        # 將數據頭指定的實際數據類型保存下來
        content_type = Response.header['Content-Type'].split('/')[1]
        # 保存 payload 中 http header 之後的全部數據
        content = Response.payload[Response.payload.index(b'\r\n\r\n') + 4]

        if "Content-Encoding" in Response.header:
            # 進行圖形解壓縮
            if Response.header["Content-Encoding"] == "gzip":
                content = zlib.decompress(Response.payload, zlib.MAX_WBITS | 32)
            elif Response.header["Content-Encoding"] == "deflate":
                content = zlib.decompress(Response.payload)
    return content, content_type

class Recapper:
    def __init__(self, fname):
        pcap = rdpcap(fname)
        # 自動切分每個 TCP 會話
        self.sessions = pcap.sessions()
        self.responses = list()

    def get_responses(self):
        # 遍歷所有數據包
        for packet in self.sessions[session]:
            try:
                # 只處理發生 80 port 接收的數據
                if packet[TCP].dport == 80 or packet[TCP].sport == 80:
                    payload += bytes(packet[TCP].payload)
            except IndexError:
                # 如果沒有成功拼接 payload 緩衝區，在螢幕列印一個 x
                sys.stdout.write('x')
                sys.stdout.flush()

            if payload:
                # 檢查 http header 的內容 
                header = get_header(payload)
                if header is None:
                    continue
                self.responses.append(Response(header=header, payload=payload))

    # 將 response 的圖片寫到輸出目錄下                
    def write(self, content_name):
        for i, response in enumerate(self.responses):
            # 提取 response 內容
            content, content_type = extract_content(response, content_name)
            if content and content_type:
                fname = os.path.join(OUTPUT, f'ex_{i}.{content_type}')
                print(f'Wrtting {fname}')   
                # 寫入文件中
                with open(fname, "wb") as f:
                    f.write(content)    

if __name__ == '__main__':
    pfile = os.path.join(PCAPS, 'pcap.pcap')
    recapper = Recapper(pfile)
    recapper.get_responses()
    recapper.write('image')