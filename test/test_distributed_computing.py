from unittest import TestCase
from source.distributed_computing import *

class TestTask(TestCase):
    def setUp(self) -> None:
        self.object=Task(lambda x : x)
    def test_SetArgs_works(self):
        self.object.setArgs([1])
    def test_run_ListStrings_works(self):
        self.object.function=lambda x,y:  x+y
        self.object.setArgs(["hello","There"])
        output=self.object()
        self.assertEqual(output,"helloThere")
    def test_run_TupleInts_works(self):
        self.object.function=lambda x,y:  x+y
        self.object.setArgs((1,2))
        self.object()
    def test_run_ListInts_works(self):
        self.object.function = lambda x, y: x + y
        self.object.setArgs([1, 2])
        self.object()
    def test_run_ArgsAndKwargs_works(self):
        def testFunc(a,b,c=None):
            a+b+c

        self.object.function=testFunc
        self.object.setArgs(["A","B"])
        self.object.setKwargs({'c':"C"})
        self.object()

    def test_setArgs_Int_RaisesTypeError(self):
        self.assertRaises(TypeError,self.object.setArgs,1)
    def test_setArgs_Char_RaisesTypeError(self):
        self.assertRaises(TypeError,self.object.setArgs,'h')
    def test_setArgs_Str_RaisesTypeError(self):
        self.assertRaises(TypeError,self.object.setArgs,"h")
    def test_setArgs_Bool_RaisesTypeError(self):
        self.assertRaises(TypeError,self.object.setArgs,True)


class TestTaskSchedulerLocal(TestCase):
    def setUp(self) -> None:
        self.object=TaskScheduler()
    def test_getput_task_works(self):
        task=Task(lambda:None)
        self.object.put(task)
        t=self.object.get()
        self.assertIsInstance(t,Task)

class TestClient(TestCase):
    def setUp(self) -> None:
        #self.object = Client()
        pass

    def test0(self):
        #self.object.connect("localhost", 5050)
        pass


class TestServer(TestCase):
    def setUp(self) -> None:
        #self.object = Server()
        pass
    def test0(self):
        pass

class TestDistributedComputeLocal(TestCase):
    def setUp(self) -> None:
        self.object=DistributedComputeLocal()
        t=Task(lambda :None)
        self.tasks=[t,t,t]
    def test_run_tasks_works(self):
        self.object.run(self.tasks)

class TestDistributedComputeRemote(TestCase):
    def setUp(self) -> None:
        #self.object=DistributedComputeRemote('localhost',8000)
        #self.object.connect()
        #t = Task(lambda: None)
        #self.tasks = [t, t, t]
        pass
    def test_run_tasks_works(self):
        #self.object.run(self.tasks)
        pass


class TestTaskEncoder(TestCase):
    def setUp(self) -> None:
        self.object=TaskEncoder()
    def test_endode_returnsBytes(self):
        bytes=self.object.encode(Task(lambda :None))

    def test_endode_decode_works(self):
        dTask=self.object.encode(Task(lambda :None))
        task=self.object.decode(dTask)
        task()

class TestDistributedComputeAPI(TestCase):
    pass

class TestDistributedComputeSlurm(TestCase):
    pass








