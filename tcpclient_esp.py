# encoding : utf-8

from socket import *
import time
import threading

# HOST = '23.105.204.132' # lijie yun
HOST = '47.101.222.148'
PORT = 6000
BUFFSIZE = 2048
ADDR = (HOST, PORT)

# tcpclientrsocket= 1
GetConnectdirection = False

global globaltcpclientrsocket
globaltcpclientrsocket = ""


# this is listen local port
def tcplisten(addr, port):
    global globaltcpclientrsocket, GetConnectdirection
    print(addr, port)
    tcplistensocket = socket(AF_INET, SOCK_STREAM)
    tcplistensocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    tcplistensocket.bind((addr, port))
    tcplistensocket.listen()

    tcplistenclientsocket, addr1 = tcplistensocket.accept()
    print("connect from {}".format(addr1))
    GetConnectdirection = True
    globaltcpclientrsocket = tcplistenclientsocket
    print(".")
    while True:
        print(".")
        time.sleep(1)


# tcpclientrsocket = socket(AF_INET,SOCK_STREAM)
# tcpclientrsocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
# tcpclientrsocket.connect(ADDR)

localaddr = ""
readytoconnect = False

while readytoconnect == False:
    tcpclientrsocket = socket(AF_INET, SOCK_STREAM)
    tcpclientrsocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    tcpclientrsocket.connect(ADDR)
    localaddr = tcpclientrsocket.getsockname()

    # send and receive data from server
    for x in range(10000):
        try:
            tcpclientrsocket.sendall("this is esp8266".encode())
            data = tcpclientrsocket.recv(BUFFSIZE).decode()
            exec("data = " + data.replace("\r", "").replace("\x00", ""))
            print(data)

            if data[0] != (1, 1) and data[1] != (1, 1):
                readytoconnect = True
                break
            time.sleep(0.3)

        except:
            # if can't get data from server, we assume it error, so close it.
            tcpclientrsocket.close()
            break

    # time.sleep(1)

# print()


print("localaddr", localaddr)
vehicle = threading.Thread(target=tcplisten, args=(localaddr))
vehicle.start()

# because esp and diannao maybe all get ip, but need first listen, then connect each other.
time.sleep(3)

tcpclientrsocket = socket(AF_INET, SOCK_STREAM)
tcpclientrsocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
# tcpclientrsocket.setsockopt(SOL_SOCKET, SO_SNDTIMEO, 5000)
# tcpclientrsocket.setsockopt(SOL_SOCKET, SO_RCVTIMEO, 5000)
connectesp = False
connectready = False
connect_trytimes = 50
while GetConnectdirection == False and connect_trytimes != 0:
    try:
        tcpclientrsocket.connect(data[1])
        print("connect to diannao ok directly")
        globaltcpclientrsocket = tcpclientrsocket
        GetConnectdirection = True
    except:
        print("connect to diannao fail once， then try again.")
        time.sleep(0.5)
        pass
    connect_trytimes -= 1

if GetConnectdirection == True:
    conecttimes = 1000
    print(" have connect diannao, so send data 1000 times,")
    time.sleep(2)
    while conecttimes != 0:
        try:

            globaltcpclientrsocket.sendall(("this is esp8266, times:%d" % conecttimes).encode())
            data = globaltcpclientrsocket.recv(BUFFSIZE).decode()
            print(data)
            # time.sleep(1)
        except:
            print("fail send..., try again!")
            pass
        conecttimes -= 1
else:
    print("can't connect each other. please use other method.")

    #

time.sleep(100)

tcpclientrsocket.close()
