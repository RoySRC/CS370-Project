import shutil

import InstructionDecoder
import OC
import copy
import mmap
import os
import psutil
import signal
import socket
import subprocess
import time

import numpy as np


class Client:

  def __init__(self, _host_, _port_, _dataFolder_):
    self.host = _host_  # ip of raspberry pi
    self.port = _port_  # port of raspberry pi
    self.instruction = InstructionDecoder.InstructionDecoder(0) # global decoder
    self.oc = OC.OC()   # used to assess temperature, power and other information about GPU 0
    self.ocType = None  # overclock type, determine whether doing CORE or MEMORY overclock
    self.dataFolder = _dataFolder_ # where to store the generated data for future analysis

  '''
    The following function determines whether or not the current OC progress can be terminated.
    The current OC progress can be terminated if 'limit' number of stress tests succeeded.
  '''
  def __stopOC__(self, x, limit=10):
    if len(x) >= limit:
      x_truncated = x[-limit:]  # get the last 'limit' number of elements of x
      if len(np.unique(x_truncated, axis=0)) == 1:
        return True
    return False

  '''
    The following function overclocks the core clock by repeatedly calling the '__startOC()__' 
    function after setting the ocType to 'CORE'. If at least 20 consecutive iterations have been 
    run with a certain OC profile and no error occurred or the system did not crash, then the 
    loop calling '__startOC__()' function is terminated and the core OC profile is set to the 
    value that ran successfully for 20 consecutive iterations. The '__stopOC__()' function 
    determines whether or not the current loop calling '__startOC__()' repeatedly be stopped.
  '''
  def __coreOverclock__(self):
    self.ocType = "CORE"
    x = []
    i = 0
    while True:
      print()
      print("Iteration: ", i)
      x += [self.__startOC__()]
      i += 1
      ## Check to see if OC iteration can be stopped
      if self.__stopOC__(x, 20):
        break

    self.ocType = None
    
  '''
    The following function overclocks the memory. This is done by repeatedly calling 
    '__startOC__()' function. The following function works similar to the '__coreOverclock__()' 
    function.
  '''
  def __memoryOverclock__(self):
    self.ocType = "MEMORY"
    x = []
    i = 0
    while True:
      print()
      print("Iteration: ", i)
      x += [self.__startOC__()]
      i += 1
      ## Check to see if OC iteration can be stopped
      if self.__stopOC__(x, 20):
        break

    self.ocType = None

  '''
    This function is to be called to start the auto overclocker. The function first starts 
    overclocking the core clock and then moves on to overclocking the memory clock.
  '''
  def startAutoOC(self):
    startTime = time.time()
    self.__coreOverclock__()
    self.__memoryOverclock__()
    print()
    print("Overclocking took", time.time()-startTime, "seconds")
    print()

    # cleanup the generated data
    import DataCleanup as DC
    DC.generateSortedList(self.dataFolder)

  '''
    The following function is responsible for performing the actual overclock The following 
    function first generates a default OC profile which is generally a profile with all offsets 
    set to zero. This profile is also the profile of the base system with no overclocking. 
  '''
  def __startOC__(self):
    # This function only runs the first time client is started
    self.__generateBaselineData__()

    if self.__getLastRunStatus__() == 0: # last profile caused the system to fail
      self.__openConnection__()
      print("Last Run crashed the system")
      self.instruction.setInstruction(self.__loadProfile__())
      print("\t Loading profile: ", self.instruction.getTuple())
      print("\t old:", self.instruction.getTuple())
      print("\t sending:", self.__generateResponse__().encode())
      self.client.send(self.__generateResponse__().encode())  # send the current profile to server
      self.instruction.setInstruction(int(self.client.recv(1024).decode()))  # get new OC profile
      print("\t new:", self.instruction.getTuple())
      self.__storeProfile__()
      self.client.close()


    prev_instruction = self.__loadProfile__()
    self.instruction.setInstruction(prev_instruction)
    self.instruction.setAliveStatus(0) # assume this profile will kill system
    self.instruction.setOcStatus(0) # assume this profile will fail
    self.__storeProfile__()
    self.__setLastRunStatus__(0) # assume this profile will kill system

    # old name of the instruction code datafile containing monitor information about
    # temperature, power draw and gpu operating clock.
    old_name = self.instruction.getInstructionCode()

    print("Running OC profile: ", self.instruction.getTuple())

    # Run overclock
    self.__setSystemOCProfile__()
    computeFlag, TempFlag = self.__stressSystem__()

    # if the OC did not crash system
    self.__openConnection__()
    self.__setLastRunStatus__(1)
    self.instruction.setAliveStatus(1)
    self.instruction.setOcStatus(computeFlag * TempFlag)
    self.instruction.setTemperatureStatus(TempFlag)
    self.instruction.setComputeStatus(computeFlag)
    self.__storeProfile__() # Store the current profile that worked

    current_oc_profile = copy.deepcopy(self.instruction)
    print("Current OC Profile:", self.instruction.getTuple(), "succeeded" if
    self.instruction.getOcStatus() == 1 else "\u001b[31m failed \u001b[0m")

    # send the current profile to server
    self.client.send(self.__generateResponse__().encode())
    print("Sent current OC profile to server: ", self.__generateResponse__())

    # get new OC profile
    self.instruction.setInstruction(int(self.client.recv(1024).decode()))
    print("New OC Profile:", self.instruction.getTuple())

    ## Store new profile and close connection
    self.__storeProfile__()
    self.client.close()

    # rename old npy data file generated by the monitor process
    src = '%s/%s.npy'%(self.dataFolder, old_name)
    dst = '%s/%s.npy'%(self.dataFolder,current_oc_profile.getInstructionCode())
    if os.path.exists(dst):
      print(src, "already exists, rewriting.....")
      os.remove(dst)
    os.rename(src, dst)

    # save the profile for data analysis purposes
    f1 = open(self.dataFolder + "/oc.profiles", "ab")
    f1.write((str(current_oc_profile.getInstructionCode()) + " ").encode())
    f1.close()

    return (current_oc_profile.getInstructionCode(), current_oc_profile.getOcStatus())


  '''
    This code is meant to be run only when the USER wishes to restart the algorithm. The 
    following code deletes all the configuration files and the file used to compare the accuracy 
    of the overclock to the base.
  '''
  def setupSystem(self):
    cmd  = "rm -rf ./client.last.run.config; "
    cmd += "rm -rf ./client.core.clock.iteration.config; "
    cmd += "rm -rf ./client.memory.clock.iteration.config; "
    cmd += "rm -rf ./client.last.run.status.config; "
    cmd += "rm -rf ./WEIGHT.npy; "
    cmd += "echo \"1\" > ./client.last.run.status.config"
    FNULL = open(os.devnull, 'w')
    subprocess.call(cmd, shell=True, stdout=FNULL)
    FNULL.close()

  '''
    The following function stress tests the system by creating tro processes. The first process 
    is the stress process which runs a neural network image classifier. The second process is a 
    monitor program which collects data about the system such as temperature and power draw. The 
    temperature data is used to determine whether or not the system is in a state of critical 
    temperature. If the system is in a state of critical temperature, the following function 
    gets this data from the monitor process and sends a kill signal to the stress process and a 
    SIGINT signal to the monitor process. A SIGKILL signal is sent to the stress proces to force 
    termination as we do not want to damage the GPU by letting the stress process terminate 
    gracefully. A SIGINT signal is sent to the monitor process to allow it to terminate 
    gracefully by first writing the data it collected to a file. This is done for data analysis 
    purposes. After termination of the two processes, the following function returns the 
    appropriate flags, in particular, the compute and the temperature flag.
  '''
  def __stressSystem__(self):
    computeFlag, tempFlag = (0, 0)

    f = [open('/tmp/mmap.stress', 'wb'), open('/tmp/mmap.monitor', 'wb')]
    f[0].write(str(0).encode())
    f[1].write(str(1).encode())
    _ = [_f_.close() for _f_ in f]

    f = [open('/tmp/mmap.stress', 'r+b'), open('/tmp/mmap.monitor', 'r+b')]
    mm = [mmap.mmap(_f_.fileno(), 0) for _f_ in f]

    # Start the stress and monitor processes
    processIDs = {}
    for i in range(2):
      pid = os.fork()
      if pid == 0: # child process
        if i == 0: # stress program
          os.execlp('python3', 'python3', 'Stress.py')
        elif i == 1: # monitor program
          os.execlp('python3', 'python3', 'Monitor.py', str(self.instruction.getInstructionCode()), self.dataFolder)
      else: # parent process
        if i == 0:
          processIDs['stress'] = pid
        elif i == 1:
          processIDs['monitor'] = pid

    ## Monitor the status of the system
    while True:
      if psutil.Process(processIDs['stress']).status() == 'zombie':
        # this means that the process is done and waiting to be cleaned up
        print("Waiting for stress process to be completely removed")
        os.waitpid(processIDs['stress'], 0)
        os.kill(processIDs['monitor'], signal.SIGINT)
        os.waitpid(processIDs['monitor'], 0)
        break

      else:
        # this means that the process is running and/or waiting
        mm[1].seek(0)
        if int(mm[1].readline().decode()) != 1:
          print("unsafe temperature kill stress.")
          os.kill(processIDs['stress'], signal.SIGKILL)
          break

      ## Use time.sleep to prevent this loop from using up all the
      ## cpu resources
      time.sleep(1)

    ## reset the mmap pointers
    mm[0].seek(0)
    mm[1].seek(0)

    ## get the compute anf temp flags
    computeFlag = int(mm[0].readline().decode())
    tempFlag = int(mm[1].readline().decode())

    if computeFlag == 0:
      print("\u001b[31m Compute error occurred \u001b[0m")
    if tempFlag == 0:
      print("\u001b[31m Critical temperature error \u001b[0m")

    ## Close the mmap pointers and return
    _ = [_mm_.close() for _mm_ in mm]
    _ = [_f_.close() for _f_ in f]
    return (computeFlag, tempFlag)

  '''
    The following function opens a connection to server for sending and 
    receiving messages.
  '''
  def __openConnection__(self):
    self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.client.connect((self.host, self.port))

  '''
    Set the system to the overclocked state defined in self.instruction
    As of the time of writing this, linux can only set the clock and
    memory offset for post pascal cards. This library is not designed
    to run for pre pascal cards
  '''
  def __setSystemOCProfile__(self):
    self.oc.setClockOffset(self.instruction.getClockOffset())
    self.oc.setMemoryClockOffset(self.instruction.getMemoryOffset())

  '''
    Generate response to send to the server
  '''
  def __generateResponse__(self):
    return (str(self.instruction.getInstructionCode()) + "|" + str(self.ocType))

  '''
    Get the status of the last run, 0 indicates fail, 1 indicates pass
  '''
  def __getLastRunStatus__(self):
    f = open("client.last.run.status.config", "r")
    code = f.read()
    f.close()
    return int(code)

  '''
    Set status of last run, 0 indicates fail, 1 indicates pass
  '''
  def __setLastRunStatus__(self, status):
    f = open("client.last.run.status.config", "w")
    f.write(str(status))
    f.close()

  '''
    Load an OC instruction profile from disk
  '''
  def __loadProfile__(self):
    f = open("client.last.run.config", "r")
    code = f.read()
    f.close()
    return int(code)

  '''
    Store an OC instruction profile to disk
  '''
  def __storeProfile__(self):
    f = open("client.last.run.config", "w")
    f.write(str(self.instruction.getInstructionCode()))
    f.close()

  '''
    When the client first runs, generate a default OC instruction and save it to file, 
    also stress test the base system and save the data for comparison with the overclocked system 
    after application of each OC profile.
  '''
  def __generateBaselineData__(self):
    if not os.path.exists("client.last.run.config"):
      print("Configuration file does not exist, creating one...")
      self.instruction.setInstruction(0)
      self.instruction.setOcStatus(0)  # assume current OC to fail
      self.instruction.setAliveStatus(0)
      self.instruction.setClockOffset(0)
      self.instruction.setMemoryOffset(0)
      self.instruction.setPowerOffset(0)
      self.instruction.setTemperatureStatus(0)
      self.instruction.setComputeStatus(0)
      self.__storeProfile__()

      # Set system OC profile to base, i.e. no overclock
      self.__setSystemOCProfile__()

      # Generate stress data
      subprocess.call("python3 ./GenerateBaseLineStressData.py", shell=True)

      # Create the data directory
      subprocess.call("mkdir -p " + self.dataFolder , shell=True)