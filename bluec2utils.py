#Utility functions for BlueC2
#Seperated for better organization

import os
from datetime import datetime

def create_logfile(logfilename):
        directory = os.path.dirname(logfilename)
        file_name = os.path.basename(logfilename)
        os.makedirs(directory, exist_ok=True)
        f = open(file_name, 'a')
        f.close()

def help(menu="main"):
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
    
def get_timestamp(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")