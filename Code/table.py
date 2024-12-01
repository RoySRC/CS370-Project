from prettytable import PrettyTable

'''
  The following table prints a status table of every overclock
  profile applied and whether or not the profile failed.
'''
class StatusTable:

  def __init__(self):
    self.table = PrettyTable(['Status', 
                              'Alive', 
                              'SysID', 
                              'coreOffset', 
                              'memOffset', 
                              'powOffset', 
                              'tempStat', 
                              'computeStat'])
    self.table.hrules = 1

    self.PASS = "\u001b[32mPASS\u001b[0m"
    self.FAIL = "\u001b[31mFAIL\u001b[0m"
    self.YES = "\u001b[32mYES\u001b[0m"
    self.NO = "\u001b[31mNO\u001b[0m"
    self.OK = "\u001b[32mOK\u001b[0m"
    self.CRITICAL = "\u001b[31mCRITICAL\u001b[0m"
    self.end = ''

  '''
    Print the table header
  '''  
  def printHeading(self):
    print(self.table)

  '''
    Reset the table
  '''
  def reset(self):
    self.table = PrettyTable(['Status', 
                                  'Alive', 
                                  'SysID', 
                                  'coreOffset', 
                                  'memOffset', 
                                  'powOffset', 
                                  'tempStat', 
                                  'computeStat'])
    self.table.hrules = 1
    self.end = ''

  '''
    data: parameter of type tuple or list
      0: oc_status    [boolean] [1: PASS,  0: FAIL]
      1: alive bit    [boolean] [1: YES,   0: NO]
      2: sys_id       [integer] 
      3: coreOffset   [integer]
      4: memOffset    [integer]
      5: powOffset    [integer]
      6: tempStat     [boolean] [1: ok,   0: critical]
      7: computeStat  [boolean] [1: PASS, 0: FAIL]
  '''
  def printRow(self, data):
    oc_status = self.PASS if data[0] == True else self.FAIL
    alive_status = self.YES if data[1] == True else self.NO
    sys_id = data[2]
    coreOffset = data[3]
    memOffset = data[4]
    powOffset = data[5]
    tempStat = self.OK if data[6] == True else self.CRITICAL
    computeStat = self.PASS if data[7] == True else self.FAIL
    
    self.table.add_row([oc_status, 
                        alive_status, 
                        sys_id, 
                        coreOffset, 
                        memOffset, 
                        powOffset, 
                        tempStat, 
                        computeStat])

    print( "\n".join(self.table.get_string().splitlines()[-2:]) )

    if self.end == '':
      self.end = self.table.get_string().splitlines()[-1]

    print("\033[F\033[F")

  '''
    Print end of table
  '''
  def printEnd(self):
    print(self.end)


if __name__ == "__main__":
  statusTable = StatusTable()
  statusTable.printHeading()
  data = (True, False, 1, 2, 3, 4, False, True)
  statusTable.printRow(data)
  statusTable.printEnd()
