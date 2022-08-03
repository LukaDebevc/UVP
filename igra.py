# Pravila igre:
# igra se na 2n * 2n plosci, v vsako polje gre natanko en kamen,
# Igrata dva igralca (beli in crn), ki se izmenjujeta,
# Vsako potezo igralec polozi 1 kamen svoje barve in 1 kamen sive barve,
# Izjema sta 1. in 2. poteza
# Pri 1. potezi beli polozi iskljucno kamen svoje barve
# Pri 2. potezi crn poleg kamna svoje barve polozi tut 2 siva kamna.

# Zmaga tisti igralec, ki ima vec povezav,
# povezavo tvorijo beli in crni kamni, sivi pa ne
# povezavo tvorijo kamni iste barve
# povezave se stejeo v ravnih linijah (po vrsticah, stolpcih in diagonalah)
# n kamnov v ravni liniji lastniku prenesejo n(n-1)/2 povezav


class Game:
    def __init__(self, size, ai_move=None, ai=None, ai_version=None, starting_points=0):
        self.size = size
        self.board = [[None for i in range(size)] for j in range(size)]
        
        self.move_sequence = []
        self.take_backs = []
        self.starting_colors = {0:1, 1:-1, 2:0}  # 1 := white, 0 := grey, -1 := black

        self.game_length = self.size * self.size
        self.points = starting_points

        self.ai_move = ai_move
        self.ai = ai_version if ai else False


    def count_points(self, y, x, dy, dx):
        c = 1
        color = self.board[y][x]
        while 0 <= y + c * dy < self.size and 0 <= x + c * dx < self.size:
            if color != self.board[y + c * dy][x + c * dx]:
                break
            c += 1
        return (c - 1) * c // 2

    
    def update_points(self, y, x):
        directions = [(i, j) for i in range(-1, 2) for j in range(-1, 2) if not (i == 0 == j)]
        self.points += (diff := self.board[y][x] * sum([self.count_points(y, x, d[0], d[1]) for d in directions]))  
        return diff


    def move(self, y, x):
        self.board[y][x] = self.starting_colors.get(len(self.move_sequence), (1, 0, -1, 0)[self.move % 4])  # določi barvo
        self.move_sequence.append((y, x, self.update_points(y, x)))
        # to bo verjetno potrebno dodati mehanizem za shranjevanje stanja igre (JSON)

    def which_player(self, nth_move):
        return ((((nth_move + 2) % 4) // 2) * 2 - 1 if nth_move != 1 else -1)

    def is_ai_move(self, nth_move=None):
        nth_move = len(self.move_sequence) if nth_move is None else nth_move
        return (not (self.ai is None)) and self.which_player(nth_move) == self.ai_move


    def loop(self, y, x): 
        self.move(y, x)
        while len(self.move_sequence) != self.game_length:
            if self.is_ai_move():
                y, x = self.ai(self.board)   #_________________________________________________ ALI BO TO OK !!
                self.move(y, x)
            else:
                break
        else:
            return 0  # _______________________  to bi lahko označovalo konec igre

    
    def take_back(self):
        # prepovedujem take back 1. poteze če jo je naredil ai
        # ai_move je beli := 1 in crni := -1 in beli ima prvo potezo
        while len(self.move_sequence) > self.ai_move:
            self.take_backs.append(self.move_sequence.pop())
            self.points -= self.take_backs[-1][2]
            if not self.is_ai_move(len(self.move_sequence) - 1):
                break
                
    
    def undo_take_back(self):
        while self.take_backs:
            self.move_sequence.append(self.take_backs.pop())
            self.points += self.move_sequence[-1][2]
            if not self.is_ai_move():
                break

            
    def import_game(self, file):
        # naj le posodbi nujne stvari, vse informacije vrjetno že v datoteki
        pass


