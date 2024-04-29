#!/usr/bin/python3

import socket,threading,re
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
        self.sock.bind(('127.0.0.1',self.port))
        self.sock.listen(10) #sets backlog to 10
        self.agent_count = 0

    def start(self):
        self.running = True
        listener = threading.Thread(target=self.accept_connections, daemon=True)
        listener.start()
        #Command handler
        while self.running == True:
            userin = input("> ")
            splits = userin.split(" ") #splits userinput on each space
            if userin.upper() == "QUIT" or userin.upper() == 'Q':
                self.stop()
            elif userin.upper() == "HELP" or userin == "?":
                self.help()
            elif splits[0].upper() == "SET":
                #Handles setting information
                if splits[1].upper() == "HELP":
                    self.set_help()
                elif splits[1].upper() == "TARGETS":
                    targets = splits[2].split(",")
                    for target in targets:
                        match = re.match(IP_REGEX,target)
                        if match and target not in self.targets:
                            self.targets.append(self.ip_to_agent(target))
                        elif self.agentnum_to_agent(target) != None and target not in self.targets:
                            self.targets.append(self.agentnum_to_agent(target))
                        elif target in self.targets:
                            pass #just ignores if its already been added
                        else:
                            print(target + " not a found connection")
                else:
                    print("Invalid command, use SET HELP to see valid paramaters for SET")
            elif splits[0].upper() == "CMD":
                length = len(splits)
                counter = 1
                cmd = ""
                while counter < length:
                    cmd += f"{splits[counter]} "
                    counter+=1
                cmd = cmd.strip()
                for target in self.targets:
                    target.sock.send(cmd.encode())
                    reply = target.sock.recv(1024).decode()
                    print(str(target),reply,sep="\n")
            elif userin.upper() == "SHOW CONNECTIONS" or userin.upper() == "SHOW CONNS":
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
            else:
                print("Command does not exist\n")

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
        print("SHELL <Agent # or IP>\tOpens an interactive shell on agent with specified IP")

    def set_help(self):
        #Smaller help menu specific to the SET command
        print("Usage: SET <ARG>")
        print("SET HELP\tDisplay this help menu")
        print("SET TARGETS <CSV list of target ips/agent #s>\tSets the targets to each target specified in a comma seperated list (Note: Overwrites previous targets)")

    def accept_connections(self):
        while self.running == True:
            sock,ip = self.sock.accept()
            self.agent_count+=1
            newAgent = Agent(self.agent_count,sock,ip)
            self.connections.append(newAgent)

    def ip_to_agent(self,ip):
        for agent in self.connections:
            if agent.ip == ip:
                return agent
        return None #null return if no agents match

    def agentnum_to_agent(self,agentnum):
        for agent in self.connections:
            if int(agent.number) == int(agentnum):
                return agent
        return None #null return if no agents match


def main():
    server = BlueServer(10267)
    server.start()
    
if __name__ == "__main__":
    main()
