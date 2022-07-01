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
    def __init__(self, size, ai_move = None, ai=True, ai_version=None):
        self.size
        self.board = [None for i in range(size) for j in range(size)]
        
        self.move_sequence = []
        self.starting_colors = {0:self.white, 1:self.black, 2:self.grey}

        self.end = self.size * self.size
        self.points = 0

        self.ai_move = ai_move
        self.ai = ai_version if ai else False

        
    def move(color, read=False):
        #       NAČRT
        # 1. če je igralec prišel na potezo posodobi sliko
        # 2. uprašaj igralca, če je potrebno
        # 2. uprašaj robota, če je potrebno
        # 3. posodobi seznam potez in točke
        pass

    def update_points():
        # posodobi število točk (učinkovitost ni preveč nujna, saj se izvaja le ekrat na ptezo)
        # če je neodvisno od prejšnih stanj je dovolj da se lahko pri importu točke posobijo na končni potezi 
        #   oz. so točke lahko že shranjene od prej
        pass
    
    def end():
        # naj umesniku vrne komando o zaključnem ekranu, točke ipd.
        pass
    
    def loop(self): 
        while len(self.move_sequence) != self.end:
            stop = self.move(color=self.starting_colors.get(self.move, [1, 0, -1, 0][self.move % 4]))
            if stop:
                return self.move_sequence
        else:
            self.end()
            
    def import_game(file):
        # naj le posodbi nujne stvari, vse informacije vrjetno že v datoteki
        pass
