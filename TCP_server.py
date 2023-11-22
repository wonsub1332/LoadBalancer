from collections.abc import Callable, Iterable, Mapping
import socket
import json
from threading import Thread
from typing import Any

HOST='127.0.0.1'
PORT=8080

m_register='{"cmd" : "register", "protocol" : "tcp", "port" : 9991}'
m_unregister='{"cmd" : "unregister", "protocol" : "tcp", "port" : 9991}'
m_health='{"ack":"health"}'

sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
health_sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
user_sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

class cmd_th(Thread):

    def __init__(self): 
        Thread.__init__(self)
        self.cmd_sock = sock
        self.cmd_sock.connect((HOST,PORT))

    def run(self):
        h_t=health_t()
        h_t.start()
        user=accept_user()
        user.start()
        while True:
            msg=int(input("send cmd(1:register , 2: unregister):"))
            if msg==1:
                self.cmd_sock.send(m_register.encode('utf-8'))
            elif msg==2:
                self.cmd_sock.send(m_unregister.encode('utf-8'))
            else:
                print("**input 1 or 2**")
                continue

            data= json.loads(self.cmd_sock.recv(1024).decode('utf-8'))
            print(data)

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
                    try:
                        self.cmd_sock.close()
                        user_sock.close()
                        user.join()
                    except:
                        print('no user')
                    break
                elif data.get("ack")=="failed":
                    print("Unregister failed")
                    print(data.get("msg"))
                else:
                    print("error")

class relay_t(Thread):

    def __init__(self,sock,addr):
        Thread.__init__(self)
        self.client_sock=sock
        self.client_addr=addr

    def run(self):
        while True:
            data=self.client_sock.recv(1024).decode('utf-8')
            print("USER" +str(self.client_addr[1])+" : "+ data)
            if(data=='quit'):
                break
            ret="we recv "+data
            self.client_sock.send(ret.encode('utf-8'))

class accept_user(Thread):
    def __init__(self):
        Thread.__init__(self)
        a,b=sock.getsockname()
        user_sock.bind((a,9991))
        user_sock.listen()
    def run(self):
        while True:
            client_sock, client_addr= user_sock.accept()
            relay_t(client_sock,client_addr).start()



class health_t(Thread):
    def __init__(self):
        Thread.__init__(self)
    def run(self):
        health_sock.connect((HOST,8081))
        while True:
            tmp=health_sock.recv(1024).decode('utf-8')
            data= json.loads(tmp)
            if(data.get('cmd')=='health'):
                print("server still a live")
            
            health_sock.send(m_health.encode('utf-8'))

            

cmd=cmd_th()


cmd.start()

