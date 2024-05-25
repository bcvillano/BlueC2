class Agent:

#Contains state and behavior for server-side handling of clients

    __slots__ = ["sock","ip","number","ipaddr","pubkey"]

    def __init__(self,number,sock,ip,pubkey):
        self.number = number
        self.ip = ip
        self.sock = sock #socket
        self.ipaddr = self.ip[0]
        self.pubkey = pubkey

    def __str__(self) -> str:
        return '{' + f"Agent #{self.number},IP={self.ip}" + "Pubkey=" + str(self.pubkey) + "}"

    def disconnect(self):
        pass