from scapy.sendrecv import sniff

def packet_callback(packet):
    print(packet.show())

def main():
    # 嗅探所有網卡，不帶任何過濾條件
    sniff(prn=packet_callback, count=1)

if __name__ == '__main__':
    main()