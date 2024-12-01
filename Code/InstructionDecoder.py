'''
    The purpose of this class is to take in as input an overclock instruction code and decode it
    and return the appropriate values using the getters. For more information regarding the
    instruction codes refer to the manual. The instruction code is a 41 bit integer.

    The zeroth
    bit represents the computation error status. A value of zero for this position represents
    failure in computation, a value of one means that the computation was successful. The first
    bit is the temperature status bit. A value of 1 for this bit means that the system is running
    under safe temperatures, whereas a value of 0 means that the system is running under critical
    temperatures. The next 7 bits ranging from bit 2 to bit 8 represents the power offset the
    current OC profile is applying. The next 11 bits, ranging from 9 to 19, represents the memory
    clock offset applied by the OC profile. Bits 20 to 30 represents the core clock offset,
    bits 31 to 38 represents the system ID (this is for future expandability of the algorithm to
    overclocking multiple systems at once instead of one system at a time). Bit 39 and 40
    represent the alive status and the OC status. A value of 1 for the alive status bit means
    that the system did not crash when stress testing with the OC profile, a value of 0 means
    that the system crashed when stress testing with the profile. A value of 1 for the OC status
    means that the current OC profile passed the stress test; a value of 0 means that the profile
    failed the stress test.
'''

class InstructionDecoder:
    
    def __init__ (self, _x_):
        self.x = _x_    ## This is the instruction code.
        self.__set_internal_values__()
    
    '''
        Getters
    '''
    def getOcStatus(self):
        return self.ocStat

    def getAliveStatus(self):
        return self.alive

    def getSystemID(self):
        return self.sysID

    def getClockOffset(self):
        return self.clockOffset

    def getMemoryOffset(self):
        return self.memOffset

    def getPowerOffset(self):
        return self.powerOffset

    def getTemperatureStatus(self):
        return self.tempStat

    def getComputeStatus(self):
        return self.compStat

    def getInstructionCode(self):
        return self.x

    def getTuple(self):
        return (
                    self.getOcStatus(),
                    self.getAliveStatus(),
                    self.getSystemID(),
                    self.getClockOffset(),
                    self.getMemoryOffset(),
                    self.getPowerOffset(),
                    self.getTemperatureStatus(),
                    self.getComputeStatus()
                )
    
    '''
        Setters
    '''

    '''
        The following function sets the values of the getters by extracting them from 'self.x'
    '''
    def __set_internal_values__(self):
        self.compStat       = (self.x & (1 << 0)) >> 0
        self.tempStat       = (self.x & (1 << 1)) >> 1
        self.powerOffset    = (self.x & (127 << 2)) >> 2
        self.memOffset      = (self.x & (2047 << 9)) >> 9
        self.clockOffset    = (self.x & (2047 << 20)) >> 20
        self.sysID          = (self.x & (255 << 31)) >> 31
        self.alive          = (self.x & (1 << 39)) >> 39
        self.ocStat         = (self.x & (1 << 40)) >> 40

    '''
        The following function sets the instruction code to decode. For more information 
        regarding the instruction code, refer to the manual.
    '''
    def setInstruction(self, _x_):
        self.x = _x_
        self.__set_internal_values__()

    def setOcStatus(self, ocStat):
        self.ocStat = ocStat
        self.__setAll__()

    def setAliveStatus(self, alive):
        self.alive = alive
        self.__setAll__()

    def setSystemID(self, sysID):
        self.sysID = sysID
        self.__setAll__()

    def setClockOffset(self, clockOffset):
        self.clockOffset = clockOffset
        self.__setAll__()

    def setMemoryOffset(self, memOffset):
        self.memOffset = memOffset
        self.__setAll__()

    def setPowerOffset(self, powerOffset):
        self.powerOffset = powerOffset
        self.__setAll__()

    def setTemperatureStatus(self, tempStat):
        self.tempStat = tempStat
        self.__setAll__()

    def setComputeStatus(self, compStat):
        self.compStat = compStat
        self.__setAll__()
        
        
    '''
        SetAll
    '''
    def __setAll__(self):
        self.x = 0
        self.x |= self.compStat << 0
        self.x |= self.tempStat << 1
        self.x |= self.powerOffset << 2
        self.x |= self.memOffset << 9
        self.x |= self.clockOffset << 20
        self.x |= self.sysID << 31
        self.x |= self.alive << 39
        self.x |= self.ocStat << 40
