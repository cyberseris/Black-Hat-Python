import socket
import threading

bind_ip = "0.0.0.0"
bind_port = 9999

server = socket.socket(socket.AF_INET, socket.SOCKET_STREAM)

server.bind((bind_ip, bind_port))

server.listen(5)

print("[*] Listening on %s:%d" % (bind_ip, bind_port))

# client handling thread
def handle_client(client_socket):
    request = client_socket.recv(1024) # 因為是 server 端

    print("[*] Received: %s" % request)

    # 回傳封包
    client_socket.send(b"ACK!")
    print(client_socket.getpeername())
    client_socket.close()

while True:
    client, addr = server.accept()

    print("[*] Accepted connection from %s:%d" %(add[0], add[1]))

    client_handler = threading.Thread(target=handle_client, args=(client,))
    client_handler.start()




