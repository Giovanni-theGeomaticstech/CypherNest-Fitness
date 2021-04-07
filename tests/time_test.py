import time
import numpy as np

size_of_vec = 10

def pure_python_version():
    print("running pure python")
    t1 = time.time()
    X = range(size_of_vec)
    Y = range(size_of_vec)
    Z = [X[i] + Y[i] for i in range(len(X)) ]
    return time.time() - t1

def numpy_version():
    print("running Numpy")
    t1 = time.time()
    X = np.arange(size_of_vec) # Create an array of that range
    Y = np.arange(size_of_vec)
    Z = X + Y
    return time.time() - t1

def functional_pure_python():
    t1 = time.time()
    array = np.arange(size_of_vec)
    print(f"Original: {array}, reduced:{[item - 100 for item in array]}")
    return time.time() - t1


def functional_numpy():
    t1 = time.time()
    array = np.arange(size_of_vec)
    print(f"Original: {array}, reduced: {array - 100}")
    return time.time() - t1


t1 = pure_python_version()
t2 = numpy_version()
t3 = functional_pure_python()
t4 = functional_numpy()
print(t1, t2)
print(t3, t4)
print("Numpy is in this example " + str(t1/t2) + " faster!")
print("Numpy functional " + str(t3/t4) + " faster!")