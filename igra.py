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
import robot


def n_to_pra(n, pra=[3, 2]):
    i = pra[0]
    while len(pra) - 1 < n:
        k = 1
        while pra[k] ** 2 <= i:
            if i % pra[k] == 0:
                break
            else:
                k += 1
        else:
            pra.append(i)
        i += 2
    pra[0] = i
    return pra[n]


def hash_geslo(str0):
    # hash() ni konsistenten za "str"
    s = 1
    for i, j in enumerate(str0):
        s *= pow(n_to_pra(i + 2), (ord(j)), 2 ** 32)
    return hash(s)


class Game:
    def __init__(
        self,
        size_y,
        size_x,
        player1=None,
        player2=None,
        ai_move=None,
        ai_version=None,
        starting_points=None,
    ):
        self.date = None
        self.comment = ""
        self.player1 = player1
        self.player2 = player2
        self.y = size_y
        self.x = size_x
        self.board = [[None for i in range(self.y)] for j in range(self.x)]

        self.move_sequence = []
        self.take_backs = []
        self.starting_colors = {0: 1, 1: -1, 2: 0}  # 1 := white, 0 := grey, -1 := black
        self.game_length = self.y * self.x

        self.ai_move = ai_move
        self.ai = ai_version if not ai_move is None else False

        if starting_points is None:
            self.points = [0, 0]
        else:
            self.points = starting_points

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
        # directions = [(i, j) for i in range(-1, 2) for j in range(-1, 2) if not (i == 0 == j)]
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
        return self.starting_colors.get(
            len(self.move_sequence), (1, 0, -1, 0)[len(self.move_sequence) % 4]
        )

    def which_player(self, nth_move=None):
        nth_move = nth_move if not (nth_move is None) else len(self.move_sequence)
        return (((nth_move + 2) % 4) // 2) * 2 - 1 if nth_move != 1 else -1

    def is_ai_move(self, nth_move=None):
        nth_move = len(self.move_sequence) if nth_move is None else nth_move
        return (not (self.ai is None)) and self.which_player(nth_move) == self.ai_move

    def loop(self, y=None, x=None):
        if self.take_backs:
            if self.take_backs[-1][0] == y and self.take_backs[-1][1] == x:
                self.undo_take_back()
            else:
                self.take_backs = []
        if (not (y is None)) and (not (x is None)):
            self.move(y, x)
        li = []
        while len(self.move_sequence) != self.game_length:
            if self.is_ai_move() and not li:
                li = robot.ai(
                    self.move_sequence, self.y, self.x, self.ai
                )  # _________________________________________________ ALI BO TO OK !!
            elif li:
                y, x = li.pop()
                self.move(y, x)
            else:
                break

    def take_back(self):
        # prepovedujem take back 1. poteze če jo je naredil ai
        # ai_move je beli := 1 in crni := -1 in beli ima prvo potezo

        while len(self.move_sequence) > (-1 if self.ai_move is None else self.ai_move):
            self.take_backs.append(self.move_sequence.pop())
            self.points[
                self.which_player(len(self.move_sequence)) // 2
            ] -= self.take_backs[-1][2]
            self.board[self.take_backs[-1][0]][self.take_backs[-1][1]] = None
            if not self.is_ai_move(len(self.move_sequence)) or (
                not self.ai_move is None
            ):
                break
        else:
            return 0
        # else:
        #     self.take_backs.append(self.move_sequence.pop())
        #     self.points[
        #         (self.which_player(len(self.move_sequence)) - 1) // 2
        #     ] -= self.take_backs[-1][2]
        #     self.board[self.take_backs[-1][0]][self.take_backs[-1][1]] = None

    def undo_take_back(self):
        # while self.take_backs:
        c = self.which_stone()
        self.move_sequence.append(self.take_backs.pop())
        self.board[self.move_sequence[-1][0]][self.move_sequence[-1][1]] = c
        self.points[
           self.which_player(len(self.move_sequence)) // 2
        ] += self.move_sequence[-1][2]
        #    if not self.is_ai_move():
        #        break

    def import_game(self, dict0):
        for key in dict0:
            setattr(self, key, dict0[key])
        return self
        

    def dump(self, comment):
        dict0 = self.__dict__
        dict0["date"] = datetime.now()
        dict0["comment"] = comment
        return dict0


class Uporabnik:
    def __init__(self, ime=None, geslo=""):
        self.ime = ime
        self.geslo = hash_geslo(geslo)
        self.igre = []
        self.vsa_zgodovina = {}
        self.argumenti = {
            "nasprotnik": 1,
            "uporabnik": ime,
            "tezavnost": 1,
            "velikost": 6,
            "barva": 0,
            "trenutna_igra": None,
            "napacno_geslo": 7,
        }

    def prijava(self, ime, geslo, datoteka1="racuni.json", datoteka2="igre.json"):
        with open(datoteka1) as racuni:
            racuni = json.load(racuni)

        if racuni.get(ime, None) is None:
            return 5

        else:
            if racuni[ime]["geslo"] == hash_geslo(geslo):
                for kljuc in racuni[ime]:
                    setattr(self, kljuc, racuni[ime][kljuc])

                if not self.argumenti["trenutna_igra"] is None:
                    self.argumenti["trenutna_igra"] = Game(1, 1).import_game(
                        self.argumenti["trenutna_igra"]
                    )

                with open(datoteka2) as igre:
                    self.vsa_zgodovina = json.load(igre)

                self.igre = sorted(
                    self.vsa_zgodovina.get(self.ime, []), key=lambda x: x.date
                )
                return None

            else:
                return 1

    def registacija(self, ime, geslo, ponovljeno_geslo, datoteka="racuni.json"):
        print(ime, geslo, ponovljeno_geslo)
        with open(datoteka) as racuni:
            racuni = json.load(racuni)

        if racuni.get(ime, None) is None and geslo == ponovljeno_geslo:
            racuni[ime] = Uporabnik(ime, geslo).__dict__
            with open(datoteka, "w", encoding="UTF-8") as d:
                print(json.dumps(racuni), file=d)
            self.prijava(ime, geslo)

        else:
            r = 1
            if not racuni.get(ime, None) is None:
                r *= 2
            if geslo != ponovljeno_geslo:
                r *= 3
            return r

    def odjava(self, datoteka="racuni.json"):
        if self.ime == None:
            return

        with open(datoteka) as d:
            racuni = json.load(d)
        racuni[self.ime] = self.__dict__
        if not self.argumenti["trenutna_igra"] is None:
            racuni[self.ime]["argumenti"]["trenutna_igra"] = (
                racuni[self.ime]["argumenti"]["trenutna_igra"].__dict__
            )
        racuni[self.ime]["igre"] = []
        racuni[self.ime]["vsa_zgodovina"] = {}

        with open(datoteka, 'w') as d:
            print(json.dumps(racuni) ,file=d)

        # to ni dokoncano

    def shrani_pozicijo(self, komentar, datoteka="igre.json"):
        for i in (
            self.argumenti["trenutna_igra"].player1,
            self.argumenti["trenutna_igra"].player2,
        ):
            if self.vsa_zgodovina[i]:
                self.vsa_zgodovina[i] += [
                    self.argumenti["trenutna_igra"].dump(komentar)
                ]
            else:
                self.vsa_zgodovina[i] = [self.argumenti["trenutna_igra"].dump(komentar)]

        with open(datoteka, "w", encoding="UTF-8") as d:
            print(json.dumps(self.vsa_zgodovina), file=d)
