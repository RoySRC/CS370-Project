import numpy as np
import sys, time, signal
sys.path.append("../Code")
from OC import OC

def signal_handler(signal, frame):
    global interrupted
    interrupted = True

signal.signal(signal.SIGINT, signal_handler)
print("monitor process started")

interrupted = False
gpu_core_utilization = []
gpu_mem_utilization = []
while True:
    gpu_core_utilization += [OC().getCurrentGPUUtilization()]
    gpu_mem_utilization += [OC().getCurrentMemoryUtilization()]
    time.sleep(1)

    if interrupted:
        np.save('/tmp/'+sys.argv[1], [gpu_core_utilization, gpu_mem_utilization])
        break

print("monitor process terminating")