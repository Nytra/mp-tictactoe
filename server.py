import socket, threading, time, select, random

class Client:
    def __init__(self, c, addr):
        print("Initialising client object", addr)
        self.data_buf = 4096
        self.opponent = None
        self.my_turn = False
        self.counter = ""
        self.c = c
        #self.c.setblocking(0)
        self.addr = addr
        self.alive = True
        # self.start()

    def get_data(self):
        #ready = select.select([self.c], [], [], 5)
        #data = 1
        #if ready[0]:
        try:
            data = self.c.recv(self.data_buf)
            return data
        except:
            self.kill()

    def get_counter(self):
        return self.counter

    def set_counter(self, counter):
        self.counter = counter

    def get_addr(self):
        return self.addr

    def get_opponent(self):
        return self.opponent

    def set_opponent(self, addr):
        self.opponent = addr

    def kill(self):
        print("Client", self.get_addr(), "has disconnected.")
        self.c.close()
        self.alive = False

    def is_alive(self):
        if self.alive:
            return True
        else:
            return False

def listen(s):
    global clients
    while True:
        s.listen(1)
        c, addr = s.accept()
        print("Connection received. Addr:", addr)
        co = Client(c, addr)
        clients.append(co)

def print_board():
    for n in range(0, 9, 3):
        print(board[n] + "|" + board[n+1] + "|" + board[n+2] + "  ", n+1, "|", n+2, "|", n+3, sep="")

def client():
    global clients
    print("Starting client thread")
    while True:
        for client in clients:
            if client.is_alive():
                #print("Client", client.get_addr(), "is alive")
                #data = client.get_data()
                #if not data:
                    #client.kill()
                if client.get_opponent() == None:
                    for match in clients:
                        if match.get_addr() == client.get_addr():
                            continue
                        else:
                            if match.get_opponent() == None:
                                print("Matching", match.addr, client.get_addr())
                                match.set_opponent(client.get_addr())
                                client.set_opponent(match.get_addr())

                                client.c.send("ready".encode())
                                match.c.send("ready".encode())
                                winner = None
                                this_turn = random.choice((match, client))
                                match.set_counter("X")
                                client.set_counter("O")
                                while not winner:
                                    this_turn.my_turn = True
                                    this_turn.c.send("go||{}||{}".format(this_turn.get_counter(), ",".join(x for x in board)).encode())
                                    print("It is ", this_turn.get_addr(), "'s turn", sep="")
                                    index = None
                                    while index == None:
                                        data = this_turn.get_data()
                                        if not data:
                                            this_turn.kill()
                                        response = data.decode("utf-8")
                                        if int(response) in range(9):
                                            index = int(response)
                                            print("received index:", index)
                                            board[index] = this_turn.get_counter()
                                            print_board()
                                            if this_turn == match:
                                                this_turn = client
                                            else:
                                                this_turn = match
                                        else:
                                            this_turn.c.send("invalid_pos||{}||{}".format(this_turn.get_counter(), ",".join(x for x in board)).encode())

clients = []
board = [" "] * 9
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server = socket.gethostbyname(socket.gethostname())
port = 45001
s.bind((server, port))
print("Starting server...")
print("IP:", server)
print("Port:", port)
print()
try:
    tl = threading.Thread(target=listen, args=(s,))
    tl.start()
    tc = threading.Thread(target=client)
    tc.start()
    print("Successfully started all threads")
except:
    s.close()