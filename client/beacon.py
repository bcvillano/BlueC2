#!/usr/bin/python3

import socket,subprocess

class Beacon:
   #Contains client side behavior and state

   __slots__ = ["sock","running","server_ip","server_port"]

   def __init__(self,server_ip,server_port):
      self.running = False
      self.server_ip = server_ip
      self.server_port = server_port

   def connect(self):
      self.sock.connect((self.server_ip,self.server_port))

   def start(self):
      self.running = True
      self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.connect()
      while self.running == True:
         pass

   def terminate(self):
      self.running = False

def main():
   beacon = Beacon("127.0.0.1",10267)
   beacon.start()

main()