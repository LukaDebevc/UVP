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

from datetime import datetime
import json
from time import time

class Game:
    def __init__(self, size_y, size_x, player1=None, player2= None, ai_move=None, ai_version=None, starting_points=[0, 0]):
        self.date = None
        self.comment = ''
        self.player1 = player1
        self.player2 = player2
        self.y = size_y 
        self.x = size_x
        self.board = [[None for i in range(self.y)] for j in range(self.x)]
        
        self.move_sequence = []
        self.take_backs = []
        self.starting_colors = {0:1, 1:-1, 2:0}  # 1 := white, 0 := grey, -1 := black

        self.game_length = self.y * self.x
        self.points = starting_points

        self.ai_move = ai_move
        self.ai = ai_version if not ai_move is None else False

        if self.ai_move:
            self.loop()  # uprašaj robota za prvo potezo


    def count_points(self, y, x, dy, dx):
        c = 1
        color = self.board[y][x]
        while 0 <= y + c * dy < self.y and 0 <= x + c * dx < self.x:
            if color != self.board[y + c * dy][x + c * dx]:
                break
            c += 1
        return c - 1

    
    def update_points(self, y, x):
        #directions = [(i, j) for i in range(-1, 2) for j in range(-1, 2) if not (i == 0 == j)]
        if self.board[y][x] == 0:
            return 0

        directions = ((0, 1), (1, 1), (1, 0), (1, -1))
        diff = 0
        for i in directions:
            a = self.count_points(y, x, i[0], i[1])
            b = self.count_points(y, x, -i[0], -i[1])
            diff += ((a + b + 1) * (a + b) - (a * (a - 1) + b * (b - 1))) // 2
        self.points[(self.board[y][x] - 1) // 2] += diff
        return diff


    def move(self, y, x):
        if self.board[y][x] is None:
            self.board[y][x] = self.which_stone()
            self.move_sequence.append((y, x, self.update_points(y, x)))
        
            # to bo verjetno potrebno dodati mehanizem za shranjevanje stanja igre (JSON)
    
    def which_stone(self, nth_move=None):
        nth_move = nth_move if not nth_move is None else len(self.move_sequence)
        return self.starting_colors.get(len(self.move_sequence), (1, 0, -1, 0)[len(self.move_sequence) % 4])

    def which_player(self, nth_move=None):
        nth_move = nth_move if not nth_move is None else len(self.move_sequence)
        return ((((nth_move + 2) % 4) // 2) * 2 - 1 if nth_move != 1 else -1)

    def is_ai_move(self, nth_move=None):
        nth_move = len(self.move_sequence) if nth_move is None else nth_move
        return (not (self.ai is None)) and self.which_player(nth_move) == self.ai_move


    def loop(self, y, x): 
        if self.take_backs:
            if self.take_backs[-1][0] == y and self.take_backs[-1][1] == x:
                self.undo_take_back()
            else:
                self.take_backs = []

        self.move(y, x)
        li = []
        while len(self.move_sequence) != self.game_length:
            if self.is_ai_move() and not li:
                li = self.ai(self.board)   #_________________________________________________ ALI BO TO OK !!
            elif li:
                y, x = li.pop()
                self.move(y, x)

    
    def take_back(self):
        # prepovedujem take back 1. poteze če jo je naredil ai
        # ai_move je beli := 1 in crni := -1 in beli ima prvo potezo
        while len(self.move_sequence) > self.ai_move:
            self.take_backs.append(self.move_sequence.pop())
            self.points[(self.which_player(len(self.move_sequence) - 1) - 1) // 2] -= self.take_backs[-1][2]
            if not self.is_ai_move(len(self.move_sequence) - 1):
                break
                
    
    def undo_take_back(self):
        while self.take_backs:
            self.move_sequence.append(self.take_backs.pop())
            self.points[self.which_player(len(self.move_sequence))] += self.move_sequence[-1][2]
            if not self.is_ai_move():
                break

            
    def import_game(self, dict):
        for key in dict:
            setattr(self, key, dict[key])

    
    def dump(self, comment):
        dict0 = self.__dict__
        dict0['date'] = datetime.now()
        dict0['comment'] = comment
        return json.dumps(dict0)


class Uporabnik:
    def __init__(self, ime, geslo):
        self.ime = ime
        self.geslo = hash(geslo)
        self.igre = []
        self.argumenti = {}



