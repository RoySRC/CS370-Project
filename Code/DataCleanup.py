import os
import numpy as np


def generateSortedList(dataFolder):
  files = []
  modification_time = []

  for file in os.listdir(dataFolder + "/"):
    if file.endswith(".npy"):
      files += [os.path.join(dataFolder, file)]
      modification_time += [os.path.getmtime(files[-1])]

  a = np.array([files, modification_time]).T
  a = a[np.float128(a[:, 1]).argsort()]  # sort by ascending order based on the second column

  with open(dataFolder + "/sorted.list", "wb") as f:
    for i in a[:, 0]:
      f.write((i[i.rfind('/')+1:] + " ").encode())



def readDataDirectory(dataFolder):
  files = None
  with open(dataFolder + "/sorted.list", "rb") as f:
    files = f.read().decode().split(" ")
  return files[:-1]
