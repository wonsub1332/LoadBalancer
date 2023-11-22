import socket
import json
import pip._vendor.requests as requests # 그냥 vscode에서 실행시
#import requests  #venv 가상환경에서 설치 후 실행하는것이 조금도 안전하다


server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

HOST = '127.0.0.1'
PORT = 8888

server_socket.connect((HOST,PORT))

data=server_socket.recv(1024).decode('utf-8')
print("LB:" + data)
ls=data.split(",")

addr=ls[0]
port=ls[1]

url = "http://{0}:{1}/test".format(addr,port)

head = {
    "Content-Type": "application/json"
}

msg=''



while True:
    msg=input("send msg(quit : q): ")
    if(msg=='q'):
        server_socket.send("quit".encode('utf-8'))
        server_socket.close()
        break
    # data
    temp = {
        "context": msg
    }

    data = json.dumps(temp)

    response = requests.post(url, headers=head, data=data)

    print("response: ", response)
    print("response.text: ", response.text)