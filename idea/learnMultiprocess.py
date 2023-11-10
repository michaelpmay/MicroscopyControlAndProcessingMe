from multiprocessing import Pool
import time
import numpy as np
def f(x):
    return np.linalg.inv(x)

if __name__ == '__main__':
    with Pool(processes=4) as pool:         # start 4 worker processes
        result1 = pool.apply_async(f, (np.random.rand(20000,20000),))
        result2 = pool.apply_async(f, (np.random.rand(20000,20000),))
        result3 = pool.apply_async(f, (np.random.rand(20000,20000),))
        result4 = pool.apply_async(f, (np.random.rand(20000,20000),))# evaluate "f(10)" asynchronously in a single process
        print(result1.get(timeout=6000))
        print(result2.get(timeout=6000))
        print(result3.get(timeout=6000))
        print(result4.get(timeout=6000))