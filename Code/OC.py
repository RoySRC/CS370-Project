import os, subprocess, copy
import warnings
warnings.filterwarnings("ignore")

'''
  This file is to be used mostly by the client.

  The purpose of this class is to store critical information
  about gpu 0 in a system with multiple GPUs. The functions
  defined in this class will only work for NVIDIA GPUs that
  have the pascal architecture. This class is only supported
  under linux, and might not work with other OSes.
  
  This class does not bother with gathering the power 
  information of the GPU since this class is written only for
  pascal cards under linux. As of the time of writing this, 
  pascal cards under linux does not support any power 
  modification feature such as setting the max power and
  core voltage offset.
'''

class OC:

  def __init__(self):
    self.FNULL = open(os.devnull, 'w')

    cmd = "nvidia-smi -i 0 -q -d Temperature"
    output = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read().decode()
    # get shutdown temperature
    self.shutdownTemperature = copy.deepcopy(output)
    self.shutdownTemperature = [i for i in self.shutdownTemperature.split('\n')
                                if 'GPU Shutdown Temp' in i]
    self.shutdownTemperature = [i[i.index(':')+2:-2] for i in self.shutdownTemperature]
    self.shutdownTemperature = int(self.shutdownTemperature[0])
     
    # get slowdown temperature
    self.slowdownTemperature = copy.deepcopy(output)
    self.slowdownTemperature = [i for i in self.slowdownTemperature.split('\n')
                                if 'GPU Slowdown Temp' in i]
    self.slowdownTemperature = [i[i.index(':')+2:-2] for i in self.slowdownTemperature]
    self.slowdownTemperature = int(self.slowdownTemperature[0])
     
    # get max operating temperature
    try:
      self.maxOperatingTemperature = copy.deepcopy(output)
      self.maxOperatingTemperature = [i for i in self.maxOperatingTemperature.split('\n')
                                      if 'GPU Max Operating Temp' in i]
      self.maxOperatingTemperature = [i[i.index(':') + 2:-2] for i in self.maxOperatingTemperature]
      self.maxOperatingTemperature = int(self.maxOperatingTemperature[0])
    except:
      pass

  '''
    The following function sets the GPU core clock offset
    for all performance levels for pascal series of cards
    under linux. The function also returns the exit status
    of the command run to set the offset.
  '''
  def setClockOffset(self, offset):
    cmd = "nvidia-settings -a [gpu:0]/GPUGraphicsClockOffsetAllPerformanceLevels=" + str(offset)
    # cmd = "nvidia-settings -a [gpu:0]/GPUGraphicsClockOffset[1]=" + str(offset)
    return subprocess.call(cmd, shell=True, stdout=self.FNULL, stderr=self.FNULL)

  '''
    The following function sets the memory clock offset for all 
    performance levels for pascal series of cards under linux.
    The function also returns the exit status of the command run 
    to set the offset.
  '''
  def setMemoryClockOffset(self, offset):
    cmd = "nvidia-settings -a [gpu:0]/GPUMemoryTransferRateOffsetAllPerformanceLevels=" + str(offset)
    # cmd = "nvidia-settings -a [gpu:0]/GPUMemoryTransferRateOffset[1]=" + str(offset)
    return subprocess.call(cmd, shell=True, stdout=self.FNULL, stderr=self.FNULL)

  '''
    As of the time of writing this library, the following function is not
    supported for pascal series of cards under linux.
  '''
  def setPowerOffset(self, offset):
    print("This feature is not supported for pascal cards under linux.")
    pass

  '''
    The following function returns the current running temperature of
    the GPU. The units are in celsius
  '''
  def getTemperature(self):
    cmd = "nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits"
    output = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read().decode()
    return int(output.split('\n')[0])

  '''
    Returns current frequency of graphics (shader) clock in MHz
  '''
  def getCurrentGraphicsClockSpeed(self):
    cmd = "nvidia-smi --query-gpu=clocks.current.graphics --format=csv,noheader,nounits"
    output = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read().decode()
    return int(output.split('\n')[0])

  '''
    Returns current frequency of SM (Streaming Multiprocessor) clock in MHz
  '''
  def getCurrentStreamingMultiprocessorClockSpeed(self):
    cmd = "nvidia-smi --query-gpu=clocks.current.sm --format=csv,noheader,nounits"
    output = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read().decode()
    return int(output.split('\n')[0])

  '''
    Returns current frequency of memory clock on MHz
  '''
  def getCurrentMemoryClockSpeed(self):
    cmd = "nvidia-smi --query-gpu=clocks.current.memory --format=csv,noheader,nounits"
    output = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read().decode()
    return int(output.split('\n')[0])

  '''
    Returns percent of time over the past second during which one or more kernels was executing 
    on the GPU.
  '''
  def getCurrentGPUUtilization(self):
    cmd = "nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits"
    output = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read().decode()
    return int(output.split('\n')[0])

  '''
    Returns percent of time over the past second during which global (device) memory was being 
    read or written.
  '''
  def getCurrentMemoryUtilization(self):
    cmd = "nvidia-smi --query-gpu=utilization.memory --format=csv,noheader,nounits"
    output = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read().decode()
    return int(output.split('\n')[0])

  '''
    The following function returns the power draw in watts.
  '''
  def getPowerDraw(self):
    cmd = "nvidia-smi --query-gpu=power.draw --format=csv,noheader,nounits"
    output = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read().decode()
    return float(output.split('\n')[0])