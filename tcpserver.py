# encoding : utf-8

from socket import *
import gc
import threading
import time

# HOST = '23.105.204.132' # lijie yun
# HOST = '47.101.222.148' # ali gongwang
HOST = "172.25.128.70"  # ali siwang
# HOST = "127.0.0.1"
# PORTesp = 31188
# PORTdiannao = 31189

PORTesp = 6000
PORTdiannao = 6001

BUFFSIZE = 2048
ADDR_esp = (HOST, PORTesp)
ADDR_diannao = (HOST, PORTdiannao)
clientlist = [(1, 1), (1, 1)]  # first is esp connect, second is diannao connect.
clientaddrlist = [(1, 1), (1, 1)]  # 第一个0为1代表通知了电脑；第二个0为1代表通知了esp.
esphavegetip = False
diannaohavegetip = False
clientnum = 2


def receivedata(tcpclisock, addr):
    pass


def waitfornewconnect(addr1, port):
    global clientlist, clientaddrlist, esphavegetip, diannaohavegetip, clientnum
    xintiaobao = 10
    tcpserversocket = socket(AF_INET, SOCK_STREAM)
    tcpserversocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    tcpserversocket.bind((addr1, port))
    tcpserversocket.listen()
    while 1:
        clientnum = 2
        print("block wait for connection")
        tcpclisock, addr = tcpserversocket.accept()
        print("connect from{}".format(addr))

        for x in range(100000):
            # receivedata(tcpclisock, addr)

            # try:
            times_recv = 500
            data = b''
            while data == b'' and times_recv != 0:
                print(".", end="")
                data = tcpclisock.recv(BUFFSIZE)
                time.sleep(0.01)
                times_recv -= 1

            if times_recv == 0:
                print("we have not get data in 5 second, so we close the connect.")
                con_index = 0
                for s, a in clientlist:
                    if s == tcpclisock:
                        tcpclisock.close()
                        break
                    con_index += 1
                print("con_index:", con_index)
                clientlist[con_index] = (1, 1)
                clientaddrlist[con_index] = (1, 1)

                break
                # try:
                #     clientlist[1][0].close()
                # except:
                #     pass
                # try:
                #     clientlist[0][0].close()
                # except:
                #     pass
                # break
                #

            print("\nget data is: ", data)
            data = data.decode()

            # except:
            #     # we don't know who is it, so we only close this connect.
            #     print ("some happen, so close connect")
            #     tcpclisock.close()
            #     break

            # print(tcpclisock.recv(BUFFSIZE))
            # print(tcpclisock._closed)
            # clientlist.append( (tcpclisock, addr))
            if "esp8266" in data:
                clientlist[0] = (tcpclisock, addr)
                clientaddrlist[0] = (addr)
            elif "diannao" in data:
                clientlist[1] = (tcpclisock, addr)
                clientaddrlist[1] = (addr)
            else:
                pass

            # we get one string, and send current ip port to down user
            try:
                tcpclisock.sendall(str(clientaddrlist).encode())
            except:
                # if we can't send data to down user, means tcp connect is close, so we close it in server.
                # tcpclisock.close()
                if "esp8266" in data:
                    clientlist[0] = (1, 1)
                    clientaddrlist[0] = (1, 1)
                elif "diannao" in data:
                    clientlist[1] = (1, 1)
                    clientaddrlist[1] = (1, 1)
                # let's we break the for cycle.
                tcpclisock.close()
                break

            if (clientaddrlist[0] != (1, 1) and clientaddrlist[1] != (1, 1)):
                print("clientaddrlist[0] != (1, 1) and clientaddrlist[1] != (1, 1)")
                if esphavegetip == True and diannaohavegetip == True:
                    print("esphavegetip == True and diannaohavegetip == True")
                    clientnum -= 1
                    starttime = time.time()
                    while (clientnum != 0) and (time.time() - starttime) < 10:
                        print(".", end="")

                    for s, a in clientlist:
                        if s != (1,1):
                            try:
                                s.close()
                            except:
                                pass
                            break

                    # try:
                    #     clientlist[0][0].close()
                    #     clientlist[1][0].close()
                    # except:
                    #     pass
                    clientlist = [(1, 1), (1, 1)]  # first is esp connect, second is diannao connect.
                    clientaddrlist = [(1, 1), (1, 1)]
                    esphavegetip = False
                    diannaohavegetip = False
                    time.sleep(20)  # we need 20 second silence
                    break
                elif "esp8266" in data:
                    esphavegetip = True
                elif "diannao" in data:
                    diannaohavegetip = True

            # send the c

            # print ("clientlist:",clientlist)
            # for s, a in clientlist:
            #     # print (a, s._closed?"":"")
            #     if s != 1:
            #         print("s:", s)
            #         print(a, "connected" if s._closed == False else "closed")


vehicleesp = threading.Thread(target=waitfornewconnect, args=(ADDR_esp))
vehiclediannao = threading.Thread(target=waitfornewconnect, args=(ADDR_diannao))
vehicleesp.start()
vehiclediannao.start()
vehicleesp.join()
vehiclediannao.join()

# tcpclisock.close()
# data = tcpclisock.recv(BUFFSIZE).decode()

gc.collect()

# tcpserversocket.close()
