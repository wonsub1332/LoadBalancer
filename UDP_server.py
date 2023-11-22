from collections.abc import Callable, Iterable, Mapping
import socket
import json
from threading import Thread
from typing import Any

server_host='127.0.0.1'
server_port=8080

PORT=9990



m_register='{"cmd" : "register", "protocol" : "udp", "port" : '+str(PORT)+'}'
m_unregister='{"cmd" : "unregister", "protocol" : "udp", "port" : '+str(PORT)+'}'
m_health='{"ack":"health"}'

sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
user_sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
health_sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

class cmd_th(Thread):

    def __init__(self): 
        Thread.__init__(self)
        self.cmd_sock = sock
        self.cmd_sock.connect((server_host,server_port))

    def run(self):
        h_t=health_t()
        h_t.start()
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
                user=relay_t()
                if data.get("ack")=="successful":
                    print("Register complete")
                    user.start()
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

class health_t(Thread):
    def __init__(self):
        Thread.__init__(self)
    def run(self):
        health_sock.connect((server_host,8081))
        while True:
            tmp=health_sock.recv(1024).decode('utf-8')
            data= json.loads(tmp)
            if(data.get('cmd')=='health'):
                print("server still a live")
            
            health_sock.send(m_health.encode('utf-8'))

class relay_t(Thread):

    def __init__(self):
        Thread.__init__(self)
        a,b=sock.getsockname()
        user_sock.bind((a,PORT))
        print(user_sock.getsockname())

    def run(self):
        
        while True:
            data,addr=user_sock.recvfrom(1024)
            
            data=data.decode('utf-8')
            print("USER(UDP)" +str(addr)+' : '+ data)
            if(data=='quit'):
                break
            ret="we recv "+data
            user_sock.sendto(ret.encode('utf-8'),addr)



            

cmd=cmd_th()
cmd.start()
cmd.join()
