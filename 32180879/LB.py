import socket
import json
from threading import Thread
import time,datetime
from queue import Queue


class saveData():
    def __init__(self,sock,addr,port,pro):
        self.sock=sock
        self.addr=addr
        self.protocol=pro
        self.port=port
    def toString(self):
        return str(self.addr[0])+","+str(self.addr[1])+","+str(self.protocol)+","+str(self.port)
    
server_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

HOST = '127.0.0.1'
PORT = 8080

connect_address=(HOST,PORT)

API_address = (HOST, 9999)
TCP_address = (HOST, 8888)
UDP_address = (HOST, 7777)

suc='{"ack":"successful"}'
health_msg='{"cmd":"hello"}'

API_list=[]
TCP_list=[]
UDP_list=[]
session_table=[]

api_q=[]
tcp_q=[]
udp_q=[]


class accept_server(Thread):
    def __init__(self):
        Thread.__init__(self)
        server_sock.bind(connect_address)
        server_sock.listen()
    
    def run(self):
        while True:
            client_socket, client_addr= server_sock.accept()
            print("server connect success : "+str(client_addr[0])+" "+str(client_addr[1]))
            sd=saveData(client_socket,client_addr,0000,'')
            server(client_socket,client_addr,sd).start()

class accept_user(Thread):
    def __init__(self,address,li):
        Thread.__init__(self)
        self.user_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.user_sock.bind(address)
        self.user_sock.listen(10)
        self.list=li
    
    def rr(self,li):
        #===============RR=============
        if len(li)==0:
            print("no server")
        elif len(li)==1:
            info=li[0]
        else:
            info=li.pop(0)
            li.append(info)
        return info
        #==============================
    
    def run(self):
        while True:
            try:
                client_socket, client_addr= self.user_sock.accept()
            except Exception as e:
                print(e)
                time.sleep(5)
            else:
                li=None
                for session in session_table:
                    if(session[0]==client_addr):
                        li=session[1]
                        break
                print("user connect success : "+str(client_addr[0])+" "+str(client_addr[1]))
                client_socket.send('connected!'.encode('utf-8'))
                if li is not None:
                    print('already connected user')
                else:
                    li=self.rr(self.list)
                    session_table.append((client_addr,li))
                    print("session table : "+str(len(session_table)))
                user(client_socket,client_addr,li).start()
                relay(li).start()
            

class cmd_t(Thread):
    def __init__(self,cl_sock,cl_addr,sd):
        Thread.__init__(self)
        self.sock=cl_sock
        self.addr=cl_addr
        self.info=sd
    
    def cmd(self,data):
        cmd=data.get('cmd')
        if cmd == 'register':
            protocol=data.get("protocol")
            self.info.port=data.get('port')
            self.info.protocol=protocol
            print(data)
            
            try:
                if protocol=='tcp':
                    print("connecting server")
                    self.info.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                    self.info.sock.connect((self.info.addr[0],self.info.port))
                    print("connected server")
                    TCP_list.append(self.info)
                elif protocol=='api':
                    API_list.append(self.info)
                else:
                    self.info.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
                    UDP_list.append(self.info)
                
                print("register successful : "+self.info.toString())
                return suc
            except Exception as e:
                return ('{"ack":"failed","msg":%s}'%str(e))

        elif cmd == "unregister":
            protocol=data.get("protocol")

            try:
                if protocol=='tcp':
                    TCP_list.remove(self.info)
                elif protocol=='api':
                    API_list.remove(self.info)
                else:
                    UDP_list.remove(self.info)
                print("unregister successful :"+self.info.toString())
                return suc
            except Exception as e:
                return ('{"ack":"failed","msg":"%s"}'%str(e))


    def run(self):
        while True:
            try:
                inp=self.sock.recv(1024).decode('utf-8')
                data= json.loads(inp)
            except Exception as e:
                print(e)
                break
            cmd=data.get("cmd")
            ack=data.get("ack")
            if cmd:
                msg=self.cmd(data)
                self.sock.send(msg.encode('utf-8'))
                if cmd=='unregister' and msg==suc:
                    break
            
            elif ack:
                protocol=data.get("protocol")
                if ack=="hello":
                    dt = datetime.datetime.now()
                    print(dt.strftime("%H시 %M분 %S초")+" server "+str(self.addr)+" : "+ack)
                    health_t(self.sock).start()
                else:
                    if protocol=='tcp':
                        TCP_list.remove(self.info)
                    elif protocol=='api':
                        API_list.remove(self.info)
                    else:
                        UDP_list.remove(self.info)
                    print("removed :"+self.info.toString())

class health_t(Thread):
    def __init__(self,cl_sock):
        Thread.__init__(self)
        self.sock=cl_sock
    def run(self):
            time.sleep(5)
            self.sock.send(health_msg.encode('utf-8'))

class relay(Thread):
    def __init__(self,li):
        Thread.__init__(self)
        self.info=li
    def run(self):
        while True:
            try:
                tmp='{"content":"%s"}'%str(tcp_q.pop())
            except Exception:
                continue
            if self.info.protocol=='tcp':
                tmp='{"content":"%s"}'%str(tcp_q.pop())
                print("to tcp "+str(self.info.sock.getsockname()))
                self.info.sock.send(tmp.encode('utf-8'))
            elif self.info.protocol=='udp':
                tmp='{"content":"%s"}'%str(udp_q.pop())
                print("to udp "+str((self.info.addr[0],self.info.port)))
                self.info.sock.sendto(tmp.encode('utf-8'),(self.info.addr[0],self.info.port))
            else:
                tmp='{"content":"%s"}'%str(api_q.pop())
                print('api')
                
                

class server(Thread):
    def __init__(self,cl_sock,cl_addr,sd):
        Thread.__init__(self)
        self.cl_sock=cl_sock
        self.cl_addr=cl_addr
        self.info=sd
    
    def run(self):
        cmd_t(self.cl_sock,self.cl_addr,self.info).start()
        health_t(self.cl_sock).start()

class user(Thread):
    def __init__(self,cl_sock,cl_addr,li):
        Thread.__init__(self)
        self.cl_sock=cl_sock
        self.addr=cl_addr
        self.info=li

    def run(self):
        while True:
            try:
                data=self.cl_sock.recv(1024).decode('utf-8')
                print("user : "+data)
                if data=='quit':
                    session_table.remove((self.addr,self.info))
                    break
                tcp_q.append(data)
            except Exception as e:
                print(e)
                break

accept_server().start()
accept_user(TCP_address,TCP_list).start()
accept_user(UDP_address,UDP_list).start()
print("==============================================================")
print("                        server")
print("             %10s"%str(server_sock.getsockname()))
print("==============================================================")
