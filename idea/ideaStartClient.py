import socket
from distributed_computing import DistributedComputeRemoteClient,Task
host = "127.0.0.1"  # The server's hostname or IP address
port = 8003  # The port used by the server

client=DistributedComputeRemoteClient(host,port)
returnValue=client.run([Task(lambda :print('hello world'))])
print(returnValue)