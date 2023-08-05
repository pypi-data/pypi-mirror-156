import sys
import time
import psutil

MEGA = 2 ** 20
GIGA = 2 ** 30

def alloc_max_str(totaltobeleaked, memoryLeaksInSec, mbleakspertime, leaksINMB):
    '''
    Function to load memory by assigning string of requested size

    Arguments:
        memory: amount of memory to be utilized in MB
    Returns:
        a : String of size 'memory'
    '''
    i = 1
    a = ''
    while True:

        #start_time = time.time()
        end_time = (time.time())+memoryLeaksInSec
        try:
            print(i)
            a = ' ' * (int(i * ((mbleakspertime)*MEGA)))
            print("the size of a ::", sys.getsizeof(a)/MEGA)
            print("memory used inside func", (psutil.virtual_memory().used >> 20))
            if((psutil.virtual_memory().used >> 20) >= totaltobeleaked):
                print("totaltobeleaked memory", totaltobeleaked)
                print("YESSSSSSSSSSSSSSSSSSSSSSSSS!")
                break
            elif sys.getsizeof(a) / MEGA == leaksINMB:
                break

            del a
        except MemoryError:
            break
        time.sleep(end_time-time.time())
        i += 1
    return a

def pmem():
    '''
    Function to display memory statistics
    '''
    tot, avail, percent, used, free = psutil.virtual_memory()[0:5]
    tot, avail, used, free = tot / GIGA, avail / GIGA, used / GIGA, free / GIGA
    print("---------------------------------------")
    print("Memory Stats: total = %s GB \navail = %s GB \nused = %s GB \nfree = %s GB \npercent = %s"
          % (tot, avail, used, free, percent))


def memory_stress(totaltobeleaked, memoryLeaksInSec, totalDurationInSec, mbleakspertime, leaksINMB):
    '''
    Function to stress memory and display memory Stats

    Arguments:
        memory: amount of memory to be utilized in MB
        exec_time: time for which the system is supposed to keep the object

    Returns:
        a : String of size 'memory'
    '''
    pmem()
    a = alloc_max_str(totaltobeleaked, memoryLeaksInSec, mbleakspertime, leaksINMB)
    pmem()
    print("Memory Filled:")
    print("Waiting for %d sec"%(totalDurationInSec))
    return a

def apply_memory_leak(leaksINMB,totalDurationInSec, memoryLeaksInSec):
    #leaksINMB = 8000
    #totalDurationInSec = 60
    #memoryLeaksInSec = 5
    totaltobeleaked = int(int(psutil.virtual_memory().used >> 20) + int(leaksINMB))
    mbleakspertime = leaksINMB/(totalDurationInSec/memoryLeaksInSec)
    print("leaks in mb as per time ", mbleakspertime)
    print("total  size of memory to be leaked", totaltobeleaked)
    memory_stress(totaltobeleaked, memoryLeaksInSec, totalDurationInSec, mbleakspertime, leaksINMB)

#need to create a check for memory should not be greater than total from psutil.virtual_memory().total