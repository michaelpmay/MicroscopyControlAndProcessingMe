from distributed_computing import *
client=Client()
client.connect('localhost',5056)
client.socket.send(bytes('hello','utf-8'))
data=client.socket.recv(1024)
#print(data)