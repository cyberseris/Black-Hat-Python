import socket

target_host = "127.0.0.1"
target_port = 80

# 建立 socket project
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 傳送資料
client.sendto(b"AAABBBCCC", (target_host, target_port))

# 接收資料,  retrieve both data and sender information
data, addr = client.recvfrom(4096)

client.close()

print(data)