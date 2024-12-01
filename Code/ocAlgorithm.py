'''
  This file contains part of the OC algorithm to be used only by the server.
'''
import InstructionDecoder


class ocAlgorithm:

  def __init__(self):
    self.instruction = InstructionDecoder.InstructionDecoder(0)
    self.last_good_profile = None
    self.coreClockIncrement = 40
    self.memoryClockIncrement = 40

    self.maxCoreLimit = 32768
    self.maxMemoryLimit = 32768

    self.failedCoreProfiles = {}
    self.failedMemoryProfiles = {}

  '''
  The following function adjusts the increment to apply to the current profile to get a new OC 
  profile. The adjusted increments are either core or memory offset increments. The type of 
  increment to adjust depends on the 'oc_type' parameter. If this parameter is 'CORE', 
  then the core clock offset increment is adjusted. If the parameter is 'MEMORY', then the memory 
  clock offset increment is adjusted. 

  The function also sets the last good OC  profile appropriately in case of negative or zero 
  increment adjustments. In the context of this problem, a negative or zero increment implies 
  that the assumption of the last good profile was wrong, and needs to be adjusted 
  appropriately. If an OC profile failed and a negative increment is to be applied, the last 
  good profile value is assumed to be the current failed OC profile. This negative increment is 
  applied to the last good OC profile to generate a new OC profile. If this new OC profile fails, 
  the above process repeats, else the increment is set to zero and the current OC is assumed to 
  be the last good profile.
'''

  def adjustIncrements(self, oc_type):
    if not self.__pass__():

      if oc_type == "CORE":
        self.__setMaxCoreLimit__()
        self.failedCoreProfiles[self.instruction.getClockOffset()] = ''

        if self.coreClockIncrement <= 0:
          self.coreClockIncrement = -1
          self.last_good_profile = self.instruction.getInstructionCode()
          print("Last good profile: ", self.instruction.getTuple())
        else:
          while (self.__coreOutOfBounds__() or self.__coreOCTestedBefore__()) and self.coreClockIncrement != 0:
            self.coreClockIncrement //= 2
        print("Last generated core OC profile failed, setting increment to:", self.coreClockIncrement)

      if oc_type == "MEMORY":
        self.__setMaxMemoryLimit__()
        self.failedMemoryProfiles[self.instruction.getMemoryOffset()] = ''

        if self.memoryClockIncrement <= 0:
          self.memoryClockIncrement = -1
          self.last_good_profile = self.instruction.getInstructionCode()
          print("Last good profile: ", self.instruction.getTuple())
        else:
          while (self.__memoryOutOfBounds__() or self.__memoryOCTestedBefore__()) and self.memoryClockIncrement != 0:
            self.memoryClockIncrement //= 2
        print("Last generated memory OC profile failed, setting increment to:", self.memoryClockIncrement)

      self.instruction.setInstruction(self.last_good_profile)

    else:

      self.last_good_profile = self.instruction.getInstructionCode()
      print("Last good profile: ", self.instruction.getTuple())

      if oc_type == "CORE":
        if self.coreClockIncrement < 0:
          self.coreClockIncrement = 0
        while (self.__coreOutOfBounds__() or self.__coreOCTestedBefore__()) and self.coreClockIncrement != 0:
          self.coreClockIncrement //= 2

      if oc_type == "MEMORY":
        if self.memoryClockIncrement < 0:
          self.memoryClockIncrement = 0
        while (self.__memoryOutOfBounds__() or self.__memoryOCTestedBefore__()) and self.memoryClockIncrement != 0:
          self.memoryClockIncrement //= 2



  '''
  The following code generates a new OC profile given the old profile and the OC type. OC type is
  either memory or clock. OC type of clock will generate a new profile with changed core clock, and
  OC of type memory will generate a new profile with changed memory clock without changing any other
  OC value.
'''

  def generateNewProfile(self, overclockType):
    self.instruction.setOcStatus(0)  # assume OC will fail
    self.instruction.setSystemID(1)  # set the system id
    self.instruction.setAliveStatus(0)  # assume that the system will die

    i = InstructionDecoder.InstructionDecoder(self.last_good_profile)

    if overclockType == "CORE":
      self.instruction.setClockOffset(i.getClockOffset() + self.coreClockIncrement)

    if overclockType == "MEMORY":
      self.instruction.setMemoryOffset(i.getMemoryOffset() + self.memoryClockIncrement)

    self.instruction.setPowerOffset(0)  # pascal cards in linux do not support power offset
    self.instruction.setTemperatureStatus(1)  # assume that the card is running safe temps
    self.instruction.setComputeStatus(1)  # assume that there will be no error


  def __pass__(self):
    _alive_ = self.instruction.getAliveStatus()
    _oc_stat_ = self.instruction.getOcStatus()
    _temp_stat_ = self.instruction.getTemperatureStatus()
    _compute_stat_ = self.instruction.getComputeStatus()
    if _alive_ * _oc_stat_ * _temp_stat_ * _compute_stat_ == 0:
      return False
    return True


  def __setMaxCoreLimit__(self):
    self.maxCoreLimit = self.instruction.getClockOffset()


  def __setMaxMemoryLimit__(self):
    self.maxMemoryLimit = self.instruction.getMemoryOffset()


  def __memoryOutOfBounds__(self):
    i = InstructionDecoder.InstructionDecoder(self.last_good_profile)
    return i.getMemoryOffset() + self.memoryClockIncrement >= self.maxMemoryLimit


  def __coreOutOfBounds__(self):
    i = InstructionDecoder.InstructionDecoder(self.last_good_profile)
    return i.getClockOffset() + self.coreClockIncrement >= self.maxCoreLimit


  def __coreOCTestedBefore__(self):
    i = InstructionDecoder.InstructionDecoder(self.last_good_profile)
    return (i.getClockOffset() + self.coreClockIncrement) in self.failedCoreProfiles


  def __memoryOCTestedBefore__(self):
    i = InstructionDecoder.InstructionDecoder(self.last_good_profile)
    return (i.getMemoryOffset() + self.memoryClockIncrement) in self.failedMemoryProfiles