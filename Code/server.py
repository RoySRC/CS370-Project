import InstructionDecoder
import ocAlgorithm
import socket

class Server:

  def __init__(self, _host_, _port_):
    self.host = _host_  # ip of raspberry pi
    self.port = _port_

    self.serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.serv.bind((self.host, self.port))
    self.serv.listen(5)

  def start(self):
    oc_algorithm = ocAlgorithm.ocAlgorithm()
    oc_type = None

    while True:
      print("Waiting for next connection")

      # The following is a blocking call
      conn, addr = self.serv.accept()
      print('Got connection from', addr)

      data = conn.recv(1024).decode()  # receive 1024 bytes of data from client

      if not data:
        conn.close()
        print()
        continue

      # Extract information
      data_array = data.split("|")
      print(data_array)
      try:
        oc_algorithm.instruction.setInstruction(int(data_array[0]))
        oc_type = data_array[1]
      except:
        pass

      print("received: ", oc_algorithm.instruction.getTuple())

      # This is where the algorithm is modified
      oc_algorithm.adjustIncrements(oc_type)

      # generate new OC profile
      oc_algorithm.generateNewProfile(oc_type)

      # send the new OC profile to the client close the connection
      conn.send(str(oc_algorithm.instruction.getInstructionCode()).encode())
      conn.close()
      print("Sent: ", oc_algorithm.instruction.getTuple())
      print()