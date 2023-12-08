import socket

target_host = "www.google.com"
target_port = 80

# 建立 socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 連接
client.connect((target_host, target_port))

# 傳送資料
client.send(b"GET / HTTP/1.1\r\nHost: google.com\r\n\r\n")

# 接收資料, received from the peer with which the socket is connected
response = client.recv(4096) # 因為是 client 端

client.close()

print(response)