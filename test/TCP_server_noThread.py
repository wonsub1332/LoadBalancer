import socket
import json
from threading import Thread


HOST='127.0.0.1'
PORT=8080

m_register='{"cmd" : "register", "protocol" : "tcp", "port" : 80}'
m_unregister='{"cmd" : "unregister", "protocol" : "tcp", "port" : 80}'
client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

client_socket.connect((HOST,PORT))

while True:
    print(client_socket.getsockname())
    msg=int(input("send(1:register , 2: unregister):"))
    if msg==1:
        client_socket.send(m_register.encode('utf-8'))
    elif msg==2:
        client_socket.send(m_unregister.encode('utf-8'))
    else:
        print("**input 1 or 2**")
        continue

    data= json.loads(client_socket.recv(1024).decode('utf-8'))
    if msg==1:
        if data.get("ack")=="successful":
            print("Register complete")
        elif data.get("ack")=="failed":
            print("Register failed")
            print(data.get("msg"))
        else:
            print("error")
    elif msg==2:
        if data.get("ack")=="successful":
            print("Unregister complete")
            break
        elif data.get("ack")=="failed":
            print("Unregister failed")
            print(data.get("msg"))
        else:
            print("error")


client_socket.close()