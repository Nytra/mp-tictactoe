import socket, threading, time, select, random

class Client:
    def __init__(self, c, addr):
        print("Initialising client object for", addr)
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

def game(player1, player2):

    def print_board(): # display this instance's board
        for n in range(0, 9, 3):
            print(board[n] + "|" + board[n + 1] + "|" + board[n + 2] + "  ", n + 1, "|", n + 2, "|", n + 3, sep="")

    def check_win(): # check this instance's board for a win
        empty = " "
        b = board
        winner = ""
        if b[0] == b[1] and b[0] == b[2] and b[0] != empty:
            winner = b[0]
        elif b[0] == b[3] and b[0] == b[6] and b[0] != empty:
            winner = b[0]
        elif b[0] == b[4] and b[0] == b[8] and b[0] != empty:
            winner = b[0]
        elif b[1] == b[4] and b[1] == b[7] and b[1] != empty:
            winner = b[1]
        elif b[2] == b[5] and b[2] == b[8] and b[2] != empty:
            winner = b[2]
        elif b[3] == b[4] and b[3] == b[5] and b[3] != empty:
            winner = b[3]
        elif b[6] == b[4] and b[6] == b[2] and b[6] != empty:
            winner = b[6]
        elif b[6] == b[7] and b[6] == b[8] and b[6] != empty:
            winner = b[6]
        else:
            winner = empty
        return winner.strip()

    def game_over():
        player1.c.send("over||{}||{}".format(winner, ",".join(x for x in board)).encode())
        player2.c.send("over||{}||{}".format(winner, ",".join(x for x in board)).encode())

    def next_turn(this_turn):
        if this_turn == player1:
            this_turn = player2
        else:
            this_turn = player1
        return this_turn


    board = [" "] * 9
    winner = None
    this_turn = random.choice((player1, player2)) # randomly select a player to go first

    this_turn.set_counter("X") # first turn always gets X
    if this_turn == player1:
        player2.set_counter("O")
    else:
        player1.set_counter("O")

    while not winner:
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
                print("Got position:", index + 1)
                if board[index] == " ":
                    board[index] = this_turn.get_counter()
                    print_board()
                    winner = check_win()
                    this_turn = next_turn(this_turn)
                else:
                    print("Invalid position.")
                    this_turn.c.send("invalid_pos||{}||{}".format(this_turn.get_counter(),
                                                                  ",".join(x for x in
                                                                           board)).encode())
            else:
                this_turn.c.send(
                    "invalid_pos||{}||{}".format(this_turn.get_counter(), ",".join(x for x in board)).encode())
    print(winner, "wins!")
    game_over()

def client():
    global clients
    while True:
        for client in clients:
            if client.is_alive():
                if client.get_opponent() == None:
                    for match in clients:
                        if match.get_addr() == client.get_addr():
                            continue
                        else:
                            if match.get_opponent() == None:
                                print("Matching", match.addr, "with", client.get_addr())
                                match.set_opponent(client.get_addr())
                                client.set_opponent(match.get_addr())
                                client.c.send("ready".encode()) # tell that clients to prepare for the game
                                match.c.send("ready".encode())
                                tg = threading.Thread(target=game, args=(client, match))
                                tg.start() # start the game thread

clients = []
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server = socket.gethostbyname(socket.gethostname())
port = 45001
s.bind((server, port))
print("Starting server...")
print("IP Address:", server)
print("Port:", port)
print()
try:
    tl = threading.Thread(target=listen, args=(s,))
    tl.start()
    tc = threading.Thread(target=client)
    tc.start()
    print("Server initialisation process complete.")
    print("Now listening for connections...")
except:
    s.close()