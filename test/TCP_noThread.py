import socket
import json
from threading import Thread


HOST='127.0.0.1'
PORT=8080

m_register='{"cmd" : "register", "protocol" : "tcp", "port" : 80}'
m_unregister='{"cmd" : "unregister", "protocol" : "tcp", "port" : 80}'
s1 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s2 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

s1.connect((HOST,PORT))

while True:
    msg=int(input("send(1:register , 2: unregister):"))
    if msg==1:
        s1.send(m_register.encode('utf-8'))
        a,b=s1.getsockname()
        s2.bind((a,9999))
        s2.listen()
    elif msg==2:
        s1.send(m_unregister.encode('utf-8'))
    else:
        print("**input 1 or 2**")
        continue

    data= json.loads(s1.recv(1024).decode('utf-8'))
    if msg==1:
        if data.get("ack")=="successful":
            print("Register complete")

            cl_sock,cl_addr=s2.accept()
            print(cl_addr)
            tmp=cl_sock.recv(1024).decode('utf-8')
            print("LB :"+tmp)
            print("LB addr "+str(cl_addr[0])+" :: "+str(cl_addr[1]))

    
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


s1.close()