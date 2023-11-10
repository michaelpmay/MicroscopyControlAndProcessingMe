import socket
import cloudpickle
import queue
import dask.distributed
import time
class iTask:
    def run(self):
        pass

class iDistributedCompute:
    def run(self):
        pass

    def checkStatus(self):
        pass

class iDistributedComputeAsync:
    def shedule(self):
        pass

    def checkStatus(self):
        pass

    
class Task:
    def __init__(self,function,*args,**kwargs):
        self.function=function
        self.args=args
        self.kwargs=kwargs

    def __call__(self):
        return self.function(*self.args,**self.kwargs)

    def setArgs(self,args):
        if not isinstance(args,(tuple,list)):
            raise TypeError
        self.args=args
    def setKwargs(self,kwargs):
        if not isinstance(kwargs,dict):
            raise TypeError
        self.kwargs=kwargs

class TaskScheduler:
    def __init__(self):
        self.task_queue = queue.Queue()

    def put(self, function,*args,**kwargs):
        task=Task(function,*args,**kwargs)
        self.task_queue.put(task)
    def get(self):
        return self.task_queue.get()

class Client:
    socket=None
    def __init__(self,host,port):
        self.socket=None
        self.setHost(host)
        self.setPort(port)
    def connect(self):
        self.socket = socket.socket((self.host, self.port))
        self.socket.connect((self.host,self.port))
    def close(self):
        self.socket.close()
    def send(self,bytes):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            s.sendall(bytes)
            data = s.recv(1024)
        return data
    def setPort(self,port):
        if not isinstance(port,int):
            raise TypeError
        self.port=port
    def setHost(self,host):
        if not isinstance(host,str):
            raise TypeError
        self.host=host

class Server:
    socket=None
    def __init__(self,host,port,numConnections=5):
        self.socket=socket.socket()
        self.hostname=host
        self.numConnections=numConnections
        self.port=port
    def start(self):
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((self.hostname, self.port))
                s.listen()
                conn, addr = s.accept()
                with conn:
                    print(f"Connected by {addr}")
                    while True:
                        data = conn.recv(2**10)
                        if not data:
                            break
                        conn.sendall(data)
    def setHost(self,host):
        if not isinstance(host,int):
            raise TypeError
        self.host=host

    def setPort(self,port):
        if not isinstance(port,int):
            raise TypeError
        self.port=port

class DistributedComputeServer:
    pass


class TaskEncoder():
    def encode(self,task):
        return cloudpickle.dumps(task)
    def decode(self,bTask):
        return cloudpickle.loads(bTask)

class DistributedComputeRemoteClient:
    def __init__(self,host,port):
        self.client=Client(host,port)
        self.encoder=TaskEncoder()
    def run(self,tasks):
        output=[]
        for t in tasks:
            bytesTask=self.encoder.encode(t)
            print(bytesTask)
            response=self.client.send(bytesTask)
            print('Response:{0}'.format(response))
            output.append(self.encoder.decode(response))
        return output

class DistributedComputeRemoteServer:
    def __init__(self,host,port):
        self.server=Server(host,port)
        self.encoder=TaskEncoder()

    def start(self):
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((self.server.hostname, self.server.port))
                s.listen()
                conn, addr = s.accept()
                with conn:
                    print(f"Connected by {addr}")
                    data=b""
                    while True:
                        data += conn.recv(2**10)
                        print(data)
                        if not data:
                            break
                task=self.encoder.decode(data)
                print(task)
                output=self.encoder.encode(task())
                conn.sendall(output)



class DistributedComputeLocal:
    def __init__(self):
        pass
    def run(self,tasks):
        if not  isinstance(tasks,list):
            raise TypeError
        print("LOCAL")
        currentTime=time.time()
        output=[]
        for t in tasks:
            output.append(t())
        print(time.time()-currentTime)
        return output

class DistributedComputeDaskTask:

    def __init__(self,*args):
        if len(args)==1:
            self.host_port=args[0]
        else:
            self.host_port=None
    def connect(self):
        self.client = dask.distributed.Client(self.host_port)
        self.client.upload_file('distributed_computing.py')
        self.client.upload_file('image_process.py')
    def disconnect(self):
        self.client.close()
        self.client=None
    def run(self,tasks):
        if not  isinstance(tasks,list):
            raise TypeError
        self.connect()
        print("DASKTASK")

        def runTask(task):
            return task()
        currentTime = time.time()
        futures = self.client.map(runTask, tasks)
        output = self.client.gather(futures)
        print(time.time() - currentTime)
        self.client.restart()

        self.disconnect()
        return output



