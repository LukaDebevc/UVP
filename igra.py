from datetime import datetime
import json
import robot
from PIL import Image
import os
import random


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
        s *= pow(n_to_pra(i + 2), (ord(j)), 2**32)
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
    ):
        self.date = str(datetime.now())
        self.name = None
        self.comment = ""
        self.player1 = player1
        self.player2 = player2
        self.y = size_y
        self.x = size_x
        self.board = [[None for i in range(self.x)] for j in range(self.y)]

        self.move_sequence = []
        self.take_backs = []
        self.starting_colors = {0: 1, 1: -1, 2: 0}  # 1 := white, 0 := grey, -1 := black
        self.game_length = self.y * self.x

        self.ai_move = ai_move
        self.ai = ai_version if not ai_move is None else False
        self.points = [0, 0]

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

    def save(self, datoteka="json_datoteke/trenutna_igra.json"):
        dict0 = self.dump(self.comment, False)
        with open(datoteka, "w", encoding="UTF-8") as d:
            print(json.dumps(dict0), file=d)

    def move(self, y, x):
        if self.board[y][x] is None:
            self.board[y][x] = self.which_stone()
            self.move_sequence.append((y, x, self.update_points(y, x)))

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
                )
            elif li:
                y, x = li.pop()
                self.move(y, x)
            else:
                break
        self.save()

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
            self.save()
        else:
            return 0

    def undo_take_back(self):
        c = self.which_stone()
        self.move_sequence.append(self.take_backs.pop())
        self.board[self.move_sequence[-1][0]][self.move_sequence[-1][1]] = c
        self.points[
            self.which_player(len(self.move_sequence)) // 2
        ] += self.move_sequence[-1][2]
        self.save()

    def import_game(self, dict0):
        for key in dict0:
            setattr(self, key, dict0[key])

        self.board = [y.copy() for y in self.board]
        self.move_sequence = self.move_sequence.copy()
        self.take_backs = self.take_backs.copy()
        self.points = self.points.copy()

        return self

    def dump(self, comment, pic=True):
        dict0 = self.__dict__
        dict0["date"] = str(datetime.now())
        dict0["comment"] = comment

        name = dict0["date"]
        for i in " .:-":
            name = name.replace(i, "")

        dict0["name"] = name
        if pic:
            self.picture(name)
        return dict0

    def picture(self, name, loc="static/zgodovina/"):
        images = {
            x: Image.open(y)
            for x, y in zip(
                (None, 1, -1, 0),
                (
                    "static/" + i
                    for i in ("prazno.png", "beli.png", "crni.png", "sivi.png")
                ),
            )
        }
        for i in images:
            images[i] = images[i].resize((80, 80))

        size_x = 80 * self.x + 5 * (self.x - 1)
        size_y = 80 * self.y + 5 * (self.y - 1)
        new_img = Image.new("RGB", (size_x, size_y), (20, 20, 20))
        for y in range(self.y):
            for x in range(self.x):
                new_img.paste(images[self.board[y][x]], (x * 85, y * 85))
        new_img.save(loc + name + ".png")


class Uporabnik:
    def __init__(self, ime=None, geslo=""):
        self.ime = ime
        self.geslo = hash_geslo(geslo)
        self.vsa_zgodovina = {}
        self.argumenti = {
            "nasprotnik": 1,
            "uporabnik": ime,
            "tezavnost": 1,
            "velikost": 6,
            "barva": 0,
            "trenutna_igra": None,
            "napacno_geslo": 11,
            "zgodovina": self.vrni_igre,
        }

    def vrni_igre(self):
        return self.vsa_zgodovina.get(self.ime, {})

    def prijava(
        self,
        ime,
        geslo,
        datoteka1="json_datoteke/racuni.json",
        datoteka2="json_datoteke/igre.json",
        datoteka3="json_datoteke/odlozisce.json",
        datoteka4="json_datoteke/trenutna_igra.json",
    ):
        with open(datoteka4) as trenutno:
            trenutno = json.load(trenutno)
            if trenutno and not (
                trenutno["player1"] == "Gost" or trenutno["player2"] == "Gost"
            ):
                with open(datoteka3, "w") as odlozisce:
                    print(json.dumps(trenutno), file=odlozisce)

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

                with open(datoteka2) as d:
                    self.vsa_zgodovina = json.load(d)

                self.argumenti["zgodovina"] = self.vrni_igre
                return None

            else:
                return 1

    def registacija(
        self, ime, geslo, ponovljeno_geslo, datoteka="json_datoteke/racuni.json"
    ):
        with open(datoteka) as racuni:
            # print(racuni.readlines())
            racuni = json.loads("".join(racuni.readlines()))
        if any(
            [
                ime == i
                for i in ["Uporabnik", "Uporabnik 1", "Uporabnik 2", "Gost"]
                + [f"Računalnik, težavnostna stopnja {i}" for i in range(1, 11)]
            ]
        ):
            r = 7
        else:
            r = 1

        if racuni.get(ime, None) is None and geslo == ponovljeno_geslo and r == 1:
            racuni[ime] = Uporabnik(ime, geslo).__dict__
            racuni[ime]["argumenti"]["zgodovina"] = None

            with open(datoteka, "w", encoding="UTF-8") as d:
                print(json.dumps(racuni), file=d)
            self.prijava(ime, geslo)

        else:
            if not racuni.get(ime, None) is None:
                r *= 2
            if geslo != ponovljeno_geslo:
                r *= 3
            return r

    def odjava(
        self,
        datoteka1="json_datoteke/racuni.json",
        datoteka2="json_datoteke/odlozisce.json",
        datoteka3="json_datoteke/trenutna_igra.json",
    ):
        # if self.ime == None:
        #    return
        with open(datoteka1) as d:
            racuni = json.load(d)
        racuni[self.ime] = self.__dict__
        if not self.argumenti["trenutna_igra"] is None:
            racuni[self.ime]["argumenti"]["trenutna_igra"] = racuni[self.ime][
                "argumenti"
            ]["trenutna_igra"].__dict__
        racuni[self.ime]["igre"] = []
        racuni[self.ime]["vsa_zgodovina"] = {}
        racuni[self.ime]["argumenti"]["zgodovina"] = None

        with open(datoteka1, "w") as d:
            print(json.dumps(racuni), file=d)

        with open(datoteka2) as odlozisce:
            odlozisce = json.load(odlozisce)
            if odlozisce:
                with open(datoteka3, "w") as trenutno:
                    print(json.dumps(odlozisce), file=trenutno)

    def shrani_pozicijo(self, komentar, datoteka="json_datoteke/igre.json"):
        dict0 = self.argumenti["trenutna_igra"].dump(komentar)
        self.argumenti["trenutna_igra"] = Game(1, 1).import_game(dict0)
        for i in (
            self.argumenti["trenutna_igra"].player1,
            self.argumenti["trenutna_igra"].player2,
        ):
            if any(
                [
                    i == j
                    for j in ["Uporabnik", "Uporabnik 1", "Uporabnik 2", "Gost"]
                    + [f"Računalnik, težavnostna stopnja {i}" for i in range(1, 11)]
                ]
            ):
                continue
            if self.vsa_zgodovina.get(i, False):
                self.vsa_zgodovina[i][dict0["name"]] = dict0
            else:
                self.vsa_zgodovina[i] = {dict0["name"]: dict0}

        with open(datoteka, "w", encoding="UTF-8") as d:
            print(json.dumps(self.vsa_zgodovina), file=d)

    def izbrisi_pozicijo(
        self,
        ime_igre,
        datoteka1="json_datoteke/igre.json",
        datoteka2="static/zgodovina/",
    ):
        if self.vsa_zgodovina[self.ime].get(ime_igre, False):
            del self.vsa_zgodovina[self.ime][ime_igre]

            with open(datoteka1, "w", encoding="UTF-8") as d:
                print(json.dumps(self.vsa_zgodovina), file=d)

        os.remove(datoteka2 + ime_igre + ".png")

    def pocisti(
        self,
        datoteka1="json_datoteke/trenutna_igra.json",
        datoteka2="json_datoteke/racuni.json",
        datoteka3="json_datoteke/odlozisce.json",
    ):

        with open(datoteka1, "r") as d:
            nazadnje = json.load(d)

        if not nazadnje:
            return None

        with open(datoteka2) as racuni:
            racuni = json.load(racuni)

        igralec = 1
        if racuni.get(nazadnje["player1"], False):
            igralec *= 2
        if racuni.get(nazadnje["player2"], False):
            igralec *= 3

        if igralec != 1:
            if igralec % 2 == 0:
                racuni[nazadnje["player1"]]["argumenti"]["trenutna_igra"] = nazadnje
            if igralec % 3 == 0:
                racuni[nazadnje["player2"]]["argumenti"]["trenutna_igra"] = nazadnje

            with open(datoteka2, "w", encoding="UTF-8") as d:
                print(json.dumps(racuni), file=d)
        else:
            self.argumenti["trenutna_igra"] = Game(1, 1).import_game(nazadnje)

        with open(datoteka3, "r") as odlozisce:
            odlozisce = json.load(odlozisce)

        if odlozisce:
            with open(datoteka3, "w") as pobrisi_odlozisce:
                print("{}", file=pobrisi_odlozisce)

            with open(datoteka1, "w") as trenutno:
                print(json.dumps(odlozisce), file=trenutno)

            self.pocisti()

    def ustvari_novo_igro(self, ime, geslo):
        if self.argumenti["nasprotnik"]:
            nasprotnik = f"Računalnik, težavnostna stopnja {self.argumenti['tezavnost']}"
        elif self.argumenti["uporabnik"] is None:
            nasprotnik = "Uporabnik 2"
        else:
            if ime == "Gost":
                nasprotnik = "Gost"
            else:
                uporabnik2 = Uporabnik()
                self.argumenti["napacno_geslo"] = (
                    napaka := uporabnik2.prijava(ime, geslo)
                )
                if napaka:
                    return 1
                else:
                    nasprotnik = uporabnik2.ime
                    uporabnik2.shrani_pozicijo(
                        komentar="Pozicija je bila shranjena avtomatično, saj ste se prijavili kot nadsprotnik drugemu uporabniku."
                    )
        if self.argumenti["velikost"] > 9999:
            y = (self.argumenti["velikost"] % 1000) // 100
            x = self.argumenti["velikost"] % 100
        else:
            y = x = self.argumenti["velikost"]

        uporabnik_ime = (
            f"Uporabnik{' 1' if nasprotnik == 'Uporabnik 2' else ''}"
            if self.argumenti["uporabnik"] is None
            else self.argumenti["uporabnik"]
        )

        r = random.randint(0, 1) if not self.argumenti["barva"] else self.argumenti["barva"]
        self.argumenti["trenutna_igra"] = Game(
            size_y=y,
            size_x=x,
            player1=uporabnik_ime if r == 1 else nasprotnik,
            player2=nasprotnik if r == 1 else uporabnik_ime,
            ai_move=1 - 2 * r if self.argumenti["nasprotnik"] else None,
            ai_version=self.argumenti["tezavnost"],
        )
        return 2