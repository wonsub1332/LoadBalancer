from collections.abc import Callable, Iterable, Mapping
import socket
import json
from threading import Thread
from typing import Any
import datetime,time

server_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
health_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

HOST = '127.0.0.1'
PORT = 8080

connect_address=(HOST,PORT)

API_address = (HOST, 9999)
TCP_address = (HOST, 8888)
UDP_address = (HOST, 7777)

ad_list=[API_address,TCP_address,UDP_address]

for i in ad_list:
    print('Start up on {} port {}'.format(*i))

index=0


API_list=[]
TCP_list=[]
UDP_list=[]
session_table=[]


class saveData():
    def __init__(self,sock,addr,port):
        self.sock=sock
        self.addr=addr
        self.port=port
    def toString(self):
        return str(self.addr[0])+","+str(self.addr[1])+","+str(self.port)

class cmd_t(Thread):
    def __init__(self,cl_sock,cl_addr,sd):
        Thread.__init__(self)
        self.cl_sock=cl_sock
        self.cl_addr=cl_addr
        self.info=sd
    
    def run(self):
        health_check=health_t(self.info)
        health_check.start()
        while True:
            tmp=self.cl_sock.recv(1024).decode('utf-8')
            data= json.loads(tmp)
            cmd=data.get("cmd")
            
            if cmd == 'register':
                protocol=data.get("protocol")
                self.info.port=data.get("port")

                if protocol=='tcp':
                    TCP_list.append(self.info)
                elif protocol=='api':
                    API_list.append(self.info)
                else:
                    UDP_list.append(self.info)

                msg='{"ack":"successful"}'

                self.cl_sock.send(msg.encode("utf-8"))
                print("register successful "+self.info.toString())

            elif cmd == "unregister":
                protocol=data.get("protocol")
                port=data.get("port")
                self.info.port=port

                if protocol=='tcp':
                    TCP_list.remove(self.info)
                elif protocol=='api':
                    API_list.remove(self.info)
                else:
                    UDP_list.remove(self.info)

                
                msg='{"ack":"successful"}'
                self.cl_sock.send(msg.encode("utf-8"))
                print("unregister successful"+self.info.toString())
                health_check.join()
                self.cl_sock.close()
                break
            else:
                msg='{"ack":"failed"}'
                self.cl_sock.send(msg.encode("utf-8"))
                break

class accept_server(Thread):
    def __init__(self):
        Thread.__init__(self)
    
    def run(self):
        while True:
            client_socket, client_addr= server_sock.accept()
            print("server connect success : "+str(client_addr[0])+" "+str(client_addr[1]))
            sd=saveData(client_socket,client_addr,0000)
            cmd_t(client_socket,client_addr,sd).start()


class health_t(Thread):
    def __init__(self,sd):
        Thread.__init__(self)
        self.info=sd
    def run(self):
        h_sock,h_addr=health_sock.accept()
        while True:
            time.sleep(5)
            print('health')
            try:
                data='{"cmd":"health"}'
                h_sock.send(data.encode('utf-8'))
                tmp=h_sock.recv(1024).decode('utf-8')
                data= json.loads(tmp)
                if(data.get('ack')=='health'):
                    print("server still a live")

            except:
                print("server closed")
                for i in TCP_list:
                    if(i==self.info):
                        TCP_list.remove(i)
                for i in API_list:
                    if(i==self.info):
                        API_list.remove(i)
                for i in UDP_list:
                    if(i==self.info):
                        UDP_list.remove(i)
                break
            




class accept_user(Thread):
    def __init__(self,address):
        Thread.__init__(self)
        self.user_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.user_sock.bind(address)
        self.user_sock.listen(10)
    
    def run(self):
        while True:
            client_socket, client_addr= self.user_sock.accept()
            user(client_socket,client_addr).start()
            
            
        

class user(Thread):
    def __init__(self,cl_sock,cl_addr):
        Thread.__init__(self)
        self.cl_sock=cl_sock
        self.cl_addr=cl_addr

    def run(self):
        print("user connect success : "+str(self.cl_addr[0])+" "+str(self.cl_addr[1]))
        info=''
        list=[]
        tmp=self.cl_sock.getsockname()
        sock_port = tmp[1]
        if sock_port==9999:
            list=API_list
        elif sock_port==8888:
            list=TCP_list
        else :
            list=UDP_list
        
        #===============RR=============

        if len(list)==0:
            print("no server")
        elif len(list)==1:
            info=list[0]
        else:
            info=list[index]
            if(index==len(list)):
                index=0
            else:
                index=index+1
        
        #===========================

        data=str(info.addr[0])+','+str(info.port)
        self.cl_sock.send(data.encode('utf-8'))
        print("USER: "+self.cl_sock.recv(1024).decode('utf-8'))

        self.cl_sock.close()

server_sock.bind(connect_address)
server_sock.listen(10)

health_sock.bind((HOST,8081))
health_sock.listen(10)

accept_server().start()

accept_user(API_address).start()
accept_user(TCP_address).start()
accept_user(UDP_address).start()
