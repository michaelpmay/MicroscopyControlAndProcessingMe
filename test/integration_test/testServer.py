from distributed_computing import *

server=Server()
server.setPort(5056)
server.bind()
server.listen()
conn,addr=server.accept()
with conn:
    #print(f"Connected by {addr}")
    while True:
        data = conn.recv(1024)
        if not data:
            break
        conn.sendall(data)