# brez tega multiprocessing nagaja
if __name__ == "__main__":

    from igra import Game, Uporabnik
    import bottle
    import os

    directory_path = os.getcwd()

    uporabnik = Uporabnik()
    uporabnik.pocisti()
    argumenti = uporabnik.argumenti

    @bottle.get("/")
    def osnovni_zaslon():
        return bottle.template("osnovni_zaslon.html", argumenti=argumenti)

    @bottle.get("/nova-igra/<nasprotnik>/<velikost>/<barva>/")
    def nova_igra(nasprotnik, velikost, barva):
        return bottle.template("nova_igra.html", argumenti=argumenti)

    @bottle.post("/nova-igra-posodobi/<nasprotnik:int>/<velikost:int>/<barva:int>/")
    def nova_igra(nasprotnik, velikost, barva):
        print(nasprotnik, velikost, barva, type(nasprotnik))
        argumenti["nasprotnik"] = bool(nasprotnik)
        argumenti["tezavnost"] = nasprotnik if nasprotnik else argumenti["tezavnost"]
        argumenti["velikost"] = velikost
        argumenti["barva"] = barva
        bottle.redirect(
            f"/nova-igra/{argumenti['tezavnost'] if argumenti['nasprotnik'] else 0}"
            + f"/{argumenti['velikost']}/{argumenti['barva']}/"
        )

    @bottle.post("/dimenzije/")
    def dimenzije():
        global argumenti
        sirina = bottle.request.forms.getunicode("sirina")
        visina = bottle.request.forms.getunicode("visina")
        if not (sirina.isnumeric() and visina.isnumeric()):
            argumenti["velikost"] = 20000
            bottle.redirect(
                f"/nova-igra/{argumenti['tezavnost'] if argumenti['nasprotnik'] else 0}"
                + f"/{argumenti['velikost']}/{argumenti['barva']}/"
            )
        sirina = int(sirina)
        visina = int(visina)
        if sirina * visina % 4 == 0:
            if sirina * visina > 0:
                argumenti["velikost"] = 10000 + visina * 100 + sirina
                bottle.redirect(
                    f"/nova-igra/{argumenti['tezavnost'] if argumenti['nasprotnik'] else 0}"
                    + f"/{argumenti['velikost']}/{argumenti['barva']}/"
                )
            else:
                argumenti["velikost"] = 30000 + visina * 100 + sirina
        else:
            argumenti["velikost"] = 40000 + visina * 100 + sirina

        bottle.redirect(
            f"/nova-igra/{argumenti['tezavnost'] if argumenti['nasprotnik'] else 0}"
            + f"/{argumenti['velikost']}/{argumenti['barva']}/"
        )

    @bottle.post("/ustvari-novo-igro/")
    def ustvari_novo_igro():
        re = uporabnik.ustvari_novo_igro(
            bottle.request.forms.getunicode("uporabniskoIme"),
            bottle.request.forms.getunicode("geslo"),
        )
        if re == 1:
            bottle.redirect(
                f"/nova-igra/{argumenti['tezavnost'] if argumenti['nasprotnik'] else 0}"
                + f"/{argumenti['velikost']}/{argumenti['barva']}/"
            )
        elif re == 2:
            bottle.redirect("/trenutna-igra/")

    @bottle.post("/oddaj-potezo/<y:int>/<x:int>/")
    def oddaj_potezo(y, x):
        argumenti["trenutna_igra"].loop(y, x)  # loop
        bottle.redirect("/trenutna-igra/")

    @bottle.post("/potezo-nazaj/")
    def potezo_nazaj():
        argumenti["trenutna_igra"].take_back()
        bottle.redirect("/trenutna-igra/")

    @bottle.post("/potezo-naprej/")
    def potezo_naprej():
        argumenti["trenutna_igra"].undo_take_back()
        bottle.redirect("/trenutna-igra/")

    @bottle.get("/trenutna-igra/")
    def trenutna_igra():
        return bottle.template("trenutna_igra.html", argumenti=argumenti)

    @bottle.get("/uporabniski-racun/")
    def uporabniski_racun():
        return bottle.template("uporabniski_racun.html", argumenti=argumenti)

    @bottle.post("/prijava/")
    def uporabniski_racun_prijava():
        global argumenti
        uporabnisko_ime = bottle.request.forms.getunicode("uporabniskoIme")
        geslo = bottle.request.forms.getunicode("geslo")
        ustreza = uporabnik.prijava(uporabnisko_ime, geslo)
        if ustreza is None:
            argumenti = uporabnik.argumenti
            print(argumenti)
            bottle.redirect("/zgodovina/")
        else:
            uporabnik.argumenti["napacno_geslo"] = ustreza
            bottle.redirect("/uporabniski-racun/")

    @bottle.post("/registracija/")
    def uporabniski_racun_registracija():
        global argumenti
        uporabnisko_ime = bottle.request.forms.getunicode("uporabniskoIme")
        geslo = bottle.request.forms.getunicode("geslo")
        ponovljeno_geslo = bottle.request.forms.getunicode("ponovnoGeslo")

        ustreza = uporabnik.registacija(uporabnisko_ime, geslo, ponovljeno_geslo)
        if ustreza is None:
            argumenti = uporabnik.argumenti
            bottle.redirect("/zgodovina/")
        else:
            uporabnik.argumenti["napacno_geslo"] = ustreza
            bottle.redirect("/uporabniski-racun/")

    @bottle.post("/odjava/")
    def odjava():
        global argumenti, uporabnik
        uporabnik.odjava()
        uporabnik = Uporabnik()
        uporabnik.pocisti()
        argumenti = uporabnik.argumenti
        bottle.redirect("/uporabniski-racun/")
        # uporabniski_racun()

    @bottle.get("/zgodovina/")
    def uporabniski_racun():
        return bottle.template("zgodovina.html", argumenti=argumenti)

    @bottle.post("/shrani-pozicijo/")
    def shrani_pozicijo():
        uporabnik.shrani_pozicijo(bottle.request.forms.getunicode("komentar"))
        bottle.redirect("/trenutna-igra/")

    @bottle.post("/nadaljuj-pozicijo/<ime>/<koda:int>/")
    def nadaljuj_pozicijo(ime, koda):
        global argumenti
        shrani, izbrisi, nadaljuj = (koda % 2 == 0), (koda % 3 == 0), (koda % 5 == 0)
        if uporabnik.vsa_zgodovina[uporabnik.ime].get(ime, False):
            igra = uporabnik.vsa_zgodovina[uporabnik.ime][ime]

            if shrani:
                uporabnik.shrani_pozicijo(argumenti["trenutna_igra"].comment)

            if izbrisi:
                uporabnik.izbrisi_pozicijo(ime)

            if nadaljuj:
                argumenti["trenutna_igra"] = Game(1, 1).import_game(igra)
                bottle.redirect("/trenutna-igra/")
            else:
                bottle.redirect("/zgodovina/")

        else:
            assert False

    @bottle.route("/static/zgodovina/<filename>")
    def server_static(filename):
        return bottle.static_file(filename, root=f"{directory_path}\static\zgodovina")

    @bottle.route("/static/<filename>")
    def server_static(filename):
        return bottle.static_file(filename, root=f"{directory_path}\static")

    bottle.run(debug=True, reloader=True)
