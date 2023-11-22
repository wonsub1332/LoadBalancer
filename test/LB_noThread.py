from collections.abc import Callable, Iterable, Mapping
import socket
import json
from threading import Thread
from typing import Any


server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s2 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

HOST = '127.0.0.1'
PORT = 8080

connect_address=(HOST,PORT)

API_address = (HOST, 80)
TCP_address = (HOST, 8000)
UDP_address = (HOST, 5000)

ad_list=[API_address,TCP_address,UDP_address]

for i in ad_list:
    print('Start up on {} port {}'.format(*i))

client_sock_list=[]
client_addr_list=[]

API_list=[]
TCP_list=[]
UDP_list=[]

server_socket.bind(connect_address)
server_socket.listen(10)

client_socket, client_addr= server_socket.accept()

while True:
    tmp=client_socket.recv(1024).decode('utf-8')
    data= json.loads(tmp)
    cmd=data.get("cmd")

    if cmd == 'register':
        protocol=data.get("protocol")
        port=data.get("port")

        client_sock_list.append(client_socket)
        client_addr_list.append(client_addr)

        msg='{"ack":"successful"}'

        client_socket.send(msg.encode("utf-8"))
        
        a,b=client_addr
        s2.connect((a,9999))
        print("client addr "+str(s2.getsockname()[0])+" :: "+str(s2.getsockname()[1]))
        test="connect test...SUCCESS"
        s2.send(test.encode('utf-8'))



    elif cmd == "unregister":
        protocol=data.get("protocol")
        port=data.get("port")

        client_sock_list.remove(client_socket)
        client_addr_list.remove(client_addr)
        
        msg='{"ack":"successful"}'
        client_socket.send(msg.encode("utf-8"))
        
        break
    else:
        msg='{"ack":"failed"}'
        client_socket.send(msg.encode("utf-8"))
        break

    print(client_addr)


