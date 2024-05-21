class Agent:

#Contains state and behavior for server-side handling of clients

    __slots__ = ["sock","ip","number","ipaddr"]

    def __init__(self,number,sock,ip):
        self.number = number
        self.ip = ip
        self.sock = sock #socket
        self.ipaddr = self.ip[0]

    def __str__(self) -> str:
        return '{' + f"Agent #{self.number},IP={self.ip}" + "}"

    def disconnect(self):
        pass