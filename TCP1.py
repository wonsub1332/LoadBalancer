import socket
import json
from threading import Thread
import datetime,time

sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
user_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

m_register='{"cmd" : "register", "protocol" : "tcp", "port" : 9991}'
m_unregister='{"cmd" : "unregister", "protocol" : "tcp", "port" : 9991}'
health_msg='{"ack":"hello"}'
inter="send cmd(1:register , 2: unregister , q: quit):"

HOST = '127.0.0.1'
PORT = 8080

connect_address=(HOST,PORT)

class receiver(Thread):
    def __init__(self):
        Thread.__init__(self)

    def cmd(self,inp):
        data= json.loads(inp)
        
        cmd=data.get("cmd")
        ack=data.get("ack")
        context=data.get("content")

        if cmd:
            print("\nLoadBalancer : "+cmd+"\n"+inter,end="")
            sock.send(health_msg.encode('utf-8'))
        elif ack:
            if ack=='successful':
                print("\nLoadBalancer : "+ack+"\n"+inter,end="")
            else:
                print("\nLoadBalancer : "+ack+" , "+data.get('msg')+"\n"+inter,end="")
        
    def run(self):
        while True:
            data=sock.recv(1024).decode('utf-8')
            try:
                self.cmd(data)
            except Exception as e:
                print(e)
                break

class sender(Thread):
    def __init__(self):
        Thread.__init__(self)
    def run(self):
        while True:
            i=input(inter)
            if i=="1":
                sock.send(m_register.encode('utf-8'))
                relay().start()
            elif i=="2":
                user_sock.close()
                sock.send(m_unregister.encode('utf-8'))
            elif i=='q':
                break
            else:
                print("**input 1 or 2**")
                continue

class relay(Thread):
    def __init__(self):
        Thread.__init__(self)
        user_sock.bind((user_sock.getsockname()[0],9991))
        user_sock.listen()
        self.sock, self.addr= user_sock.accept()
    
    def run(self):
        dt = datetime.datetime.now()
        print("start time :" + dt.strftime("%H시 %M분 %S초"))
        while True:
            inp=self.sock.recv(1024).decode('utf-8')
            data= json.loads(inp)
            print("\nUser : "+data.get("content")+"\n"+inter,end="")
            if data=='qqqq':
                break
        print("end time :" + dt.strftime("%H시 %M분 %S초"))
sock.connect(connect_address)
sender().start()
receiver().start()




