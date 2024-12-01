import mmap
import sys, time, signal
from OC import OC
import numpy as np

class Monitor:

  def __init__(self, profile):
    self.ocProfile = profile
    self.oc = OC()
    self.data = []
    self.criticalTemperature = False
    self.interrupted = False
    self.interval = 1/1

  def setInterval(self, interval):
    self.interval = interval

  def sigIntHandler(self, sig, frame):
    self.interrupted = True

  def start(self):
    while True and not self.interrupted:
      temperature = self.oc.getTemperature()

      self.data += [
        [
          temperature,
          self.oc.getPowerDraw(),
          self.oc.getCurrentGraphicsClockSpeed(),
          self.oc.getCurrentStreamingMultiprocessorClockSpeed(),
          self.oc.getCurrentMemoryClockSpeed()
         ]
      ]

      if temperature >= self.oc.slowdownTemperature:
        self.criticalTemperature = True
        print("\u001b[31m GPU temp. over slowdown temp. \u001b[0m")
        break

      time.sleep(self.interval)


  def saveDataToFile(self, filename):
    np.save(filename, self.data)


if __name__ == "__main__":
  shared_file = "/tmp/mmap.monitor"
  monitor = Monitor(sys.argv[1])

  signal.signal(signal.SIGINT, monitor.sigIntHandler)

  monitor.start()

  if monitor.criticalTemperature:
    with open(shared_file, 'r+b') as f:
      mm = mmap.mmap(f.fileno(), 0)
      mm.seek(0)
      mm[:] = "0".encode()
      mm.close()

  monitor.saveDataToFile(sys.argv[2] + "/" + sys.argv[1])
