import socket

server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

HOST = '127.0.0.1'
PORT = 8888

server_socket.connect((HOST,PORT))

data=server_socket.recv(1024).decode('utf-8')
print("LB:" + data)

while True:
    msg=input("send msg(quit : q): ")
    if(msg=='q'):
        server_socket.send("quit".encode('utf-8'))
        server_socket.close()
        break
    server_socket.send(msg.encode('utf-8'))

