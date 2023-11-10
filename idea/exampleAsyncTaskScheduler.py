import threading
import queue

class Task:
    def __init__(self,function,*args,**kwargs):
        self.function=function
        self.args=args
        self.kwargs=kwargs

    def __call__(self):
        self.function(*self.args,**self.kwargs)

class TaskExecutor:
    def __init__(self):
        self.task_queue = queue.Queue()
        self.worker_thread = threading.Thread(target=self._run_tasks)
        self.worker_thread.daemon = True
        self.worker_thread.start()

    def _run_tasks(self):
        while True:
            try:
                task = self.task_queue.get()
                if task is None:
                    break  # Exit the thread when None is encountered
                task()
            except Exception as e:
                print(f"An error occurred while executing a task: {e}")
            finally:
                self.task_queue.task_done()

    def add_task(self, function,*args,**kwargs):
        task=Task(function,*args,**kwargs)
        self.task_queue.put(task)

    def wait_for_completion(self):
        self.task_queue.join()

    def stop(self):
        # Signal the worker thread to exit
        self.task_queue.put(None)
        self.worker_thread.join()

if __name__ == "__main__":
    def sample_task(task_name,secondary='hello'):
        print(f"Executing task: {task_name}")
        print(f"Executing task: {secondary}")

    executor = TaskExecutor()

    # Adding tasks to be executed in order
    executor.add_task(sample_task,("Task 1"),secondary='hello again')
    executor.add_task(sample_task,("Task 2"))
    executor.add_task(sample_task,("Task 3"))

    # Wait for all tasks to complete
    executor.wait_for_completion()

    # Stop the executor when done
    executor.stop()