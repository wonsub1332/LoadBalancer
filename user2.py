import socket
import time,datetime

server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

HOST = '127.0.0.1'
PORT = 8888

server_socket.connect((HOST,PORT))

data=server_socket.recv(1024).decode('utf-8')
print("LB:" + data)

start = time.time()
for i in range(1,1000):
    msg=str(i)
    server_socket.send(msg.encode('utf-8'))
    data=server_socket.recv(1024).decode('utf-8')
server_socket.send("qqqq".encode('utf-8'))
data=server_socket.recv(1024).decode('utf-8')
server_socket.send("quit".encode('utf-8'))
data=server_socket.recv(1024).decode('utf-8')
end = time.time()

print(f"{end - start:.5f} sec")
server_socket.close()
