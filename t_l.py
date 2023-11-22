import socket
from threading import Thread
import datetime,time

sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

HOST = '127.0.0.1'
PORT = 8080

connect_address=(HOST,PORT)

class reciver(Thread):
    def __init__(self,cl_sock,cl_addr):
        Thread.__init__(self)
        self.cl_sock=cl_sock
        self.cl_addr=cl_addr
    def run(self):
        while True:
            try:
                msg=self.cl_sock.recv(1024).decode('utf-8')
            except:
                continue
            print(msg)

class sender(Thread):
    def __init__(self,cl_sock,cl_addr):
        Thread.__init__(self)
        self.cl_sock=cl_sock
        self.cl_addr=cl_addr
    def run(self):
        while True:
            time.sleep(5)
            try:
                msg='hiwioj'
                self.cl_sock.send(msg.encode('utf-8'))
            except:
                continue



def __main__():
    print("server")
    sock.bind(connect_address)
    sock.listen()
    cl_sock,cl_addr=sock.accept()
    sender(cl_sock,cl_addr).start()
    reciver(cl_sock,cl_addr).start()

__main__()