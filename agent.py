class Agent:

#Contains state and behavior for server-side handling of clients

    __slots__ = ["sock","ip","number","ipaddr","pubkey","local_ip","tags"]

    def __init__(self,number,sock,ip):
        self.number = number
        self.ip = ip
        self.sock = sock #socket
        self.ipaddr = self.ip[0]
        self.tags = []

    def __str__(self) -> str:
        if self.local_ip == None:
            return '{' + f"Agent #{self.number},IP={self.ip}"+"}"
        else:
            return '{' + f"Agent #{self.number},IP={self.ip}" + f",Local IP={self.local_ip}" + "}"

    def display_tags(self):
        for tag in self.tags:
            print(tag)