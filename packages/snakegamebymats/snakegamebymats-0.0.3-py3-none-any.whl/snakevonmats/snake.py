import pygame
import os
import sys
from tkinter import *
from random import randrange


os.environ['SDL_VIDEO_CENTERED'] = '1' #Fenster erscheint in der Mitte des Bildschirms
pygame.init()

B = 500 # Fenster Breite
H = 350 # Fenster Höhe

ZELLEN_GROESSE = 10
SPALTEN_ANZAHL = B // ZELLEN_GROESSE
REIHEN_ANZAHL = H // ZELLEN_GROESSE

bild = r'src\bilder\green.png' # Bild für die Schlange

# RGB Farben
ROT = (255, 50, 30)
BLAU = (50, 80, 255)
SCHWARZ = (0, 0, 0)
TUERKIS = (0, 230, 230)

# Standard Shriftarten die verwendet werden
LARGE_FONT = ("Tahoma", 55)
NORM_FONT = ("Verdana", 10)
SCORE_FONT = ("Tahoma", 20)


class Waende(object):
    def liste_erstellen(self, groesse):   # Erstellt eine Liste von Wand objekten
        
        waende = [] 

        waende.append(pygame.Rect((0, 0), (B, groesse))) # Wand oben
        waende.append(pygame.Rect((B - groesse, 0), (groesse, H))) # rechte Wand
        waende.append(pygame.Rect((0, 0), (groesse, H))) # linke Wand
        waende.append(pygame.Rect((0, H - groesse), (B, groesse))) # Wand unten

        return waende


class Snake(pygame.sprite.Sprite):
    def __init__(self, img):
        super().__init__()
        self.bild = pygame.image.load(img) # setzt die Schlange mit dem Bild gleich
        # streckt das Bild über die ganze Schlange wenn diese größer wird
        self.bild = pygame.transform.scale(self.bild, (ZELLEN_GROESSE, ZELLEN_GROESSE))
        # setzt die Start position
        self.koerper = [[SPALTEN_ANZAHL // 2, REIHEN_ANZAHL // 2],
                        [SPALTEN_ANZAHL // 2, REIHEN_ANZAHL // 2 + 1],
                        [SPALTEN_ANZAHL // 2, REIHEN_ANZAHL // 2 + 2]]
        self.richtung = [-1, 0]
        self.old_key = ""
        self.speed = 15 # Tempo der Schlange
        self.leben = 3  # Wie viele Leben hat die Schlange
        self.punkte = 0 # Punkte Anzahl am Start

    
    def richtungsset(self, button):
        if self.old_key == button:
            self.speed = 20

        # Schlange kann sich nur nach oben bewegen, wenn sie sich nicht nach unten bewegt
        elif button == pygame.K_UP and self.richtung != [0, 1]:
            self.richtung = [0, -1]
            self.speed = 20

        # Schlange kann sich nur nach links bewegen, wenn sie sich nicht nach rechts bewegt
        elif button == pygame.K_LEFT and self.richtung != [1, 0]:
            self.richtung = [-1, 0]
            self.speed = 20

        # Schlange kann sich nur nach unten bewegen, wenn sie sich nicht nach oben bewegt
        elif button == pygame.K_DOWN and self.richtung != [0, -1]:
            self.richtung = [0, 1]
            self.speed = 20

        # Schlange kann sich nur nach rechts bewegen, wenn sie sich nicht nach links bewegt
        elif button == pygame.K_RIGHT and self.richtung != [-1, 0]:
            self.richtung = [1, 0]
            self.speed = 20

    def bewegen(self):
        self.koerper.insert(0, [self.koerper[0][0] + self.richtung[0],
                                self.koerper[0][1] + self.richtung[1]])
        self.koerper[0][0] = self.koerper[0][0] % SPALTEN_ANZAHL
        self.koerper[0][1] = self.koerper[0][1] % REIHEN_ANZAHL

    def anzeigen(self, screen):
        for i in self.koerper:
            screen.blit(self.bild, (i[0]*ZELLEN_GROESSE, i[1]*ZELLEN_GROESSE,
                                    ZELLEN_GROESSE, ZELLEN_GROESSE)) # Alle Bodyparts der Schlange werden gezeigt

    def nach_treffer(self):
        self.leben -= 1

        # Wenn Wandtreffer dann zum Startpunkt in der mitte zurücksetzen
        self.koerper = [[SPALTEN_ANZAHL // 2, REIHEN_ANZAHL // 2],
                     [SPALTEN_ANZAHL // 2, REIHEN_ANZAHL // 2 + 1],
                     [SPALTEN_ANZAHL // 2, REIHEN_ANZAHL // 2 + 2]]
        #Schlange zeigt wieder nach oben
        self.richtung = [0, -1]
    
    def gegen_wand(self, waende):
        treffer = False

        for wand in waende: # Sieht nach ob eine Wand getroffen wurde
            kopf = pygame.Rect(self.koerper[0][0] * ZELLEN_GROESSE,
                                self.koerper[0][1] * ZELLEN_GROESSE,
                                ZELLEN_GROESSE, ZELLEN_GROESSE)
                
            if wand.colliderect(kopf):
                self.nach_treffer()
                treffer = True

            # checkt ob die Schlange sich in sich selbst bewegt hat
            elif self.koerper[0] in self.koerper[1:]:
                self.nach_treffer()
                treffer = True
            
        return treffer


class Apfel:

    anzahl = 0

    def __init__(self, groesse):
        self.x = randrange(1, SPALTEN_ANZAHL-1) # Zufällige Position auf der x Achse
        self.y = randrange(1, REIHEN_ANZAHL-1)  # Zufällige Position auf der y Achse
        self.groesse = groesse
        self.rect = pygame.Rect(self.x * ZELLEN_GROESSE,
                                self.y * ZELLEN_GROESSE,
                                self.groesse, self.groesse)

    def anzeigen(self, screen):
        # Zeigt den Apfel in for eines Rechtecks an
        pygame.draw.rect(screen, ROT, self.rect)

    def random_xy(self):
        # ändert die Position des Apfels auf zufällige weise
        self.x = randrange(1, SPALTEN_ANZAHL-1)
        self.y = randrange(1, REIHEN_ANZAHL-1)

        self.rect.x = self.x * ZELLEN_GROESSE
        self.rect.y = self.y * ZELLEN_GROESSE

        # Jeder fünfte Apfel ist größer
        if Apfel.anzahl % 5 == 0:
            self.groesse = ZELLEN_GROESSE + 8
            self.rect.x -= 5
            self.rect.y -= 5


bildschirm = pygame.display.set_mode((B, H))    # Erstellt den Bildschirm mit den Konstanten von Höhe und breite
pygame.display.set_caption('Schlangen Spiel')

liste_waende = Waende.liste_erstellen(Waende(), ZELLEN_GROESSE) # erstellt die liste für die Wände

uhr = pygame.time.Clock() # Für das Tempo der Schlange und das Timing
spieler = Snake(bild)   # Die Schlange
apfel = Apfel(ZELLEN_GROESSE)
start = False
game_over = False
sekunden = 3

def text_ausgeben(schriftart, text, farbe, textpos=None):
    schriftart = pygame.font.SysFont(schriftart[0], schriftart[1])
    text = schriftart.render(text, 1, farbe)
    if textpos is None:
        textpos = text.get_rect(centerx = B / 2, centery = H / 2)
    bildschirm.blit(text, textpos)

def textausgabe():
    text = "Leben: {} Punkte: {} Äpfel: {}".format("+" * spieler.leben, spieler.punkte, apfel.anzahl)
    text_ausgeben(SCORE_FONT, text, TUERKIS, (10, 10))


def datei_erstellen():  # eine Datei mit den Scores wird erstellt
    try:
        d = open("ergebnisse.txt", "r")
        n = d.read().count(spieler_name) + 1
        d.close()

    except:
        d = open("ergebnisse.txt", "w")
        d.close()
        n = 0

    d = open("ergebnisse.txt", "a")
    d.write("{} {} {} \n".format(spieler_name + str(n), apfel.anzahl, spieler.punkte))
    d.close()

def waende_erstellen():
    for wand in liste_waende:
        pygame.draw.rect(bildschirm, pygame.Color("blue"), wand, 0)

def countdown():    # Countdown vor dem Spiel wird gesetzt
    global start, sekunden

    pygame.time.wait(1000)
    bildschirm.fill(SCHWARZ)
    text_ausgeben(LARGE_FONT, "{}".format(sekunden), BLAU)
    sekunden -= 1
    pygame.display.flip()

def apfel_essen():  # definiert was passiert wenn ein Apfel gegessen wird
    kopf = spieler.koerper[0]
    kopf_rect = pygame.Rect((kopf[0] * ZELLEN_GROESSE, kopf[1] * ZELLEN_GROESSE,
                            ZELLEN_GROESSE, ZELLEN_GROESSE)) # vergrößert die Schlange
    return kopf_rect.colliderect(apfel.rect)

def popup(msg):
    popupfen = Tk()    # Popup Fenster wo man seinen Namen eingeben kann

    def mitte(win):     # Popup wird in der Mitte des Bildschirms angezeigt
        win.update_idletasks()
        breite = win.winfo_width()
        hoehe = win.winfo_height()
        x = (win.winfo_screenwidth() // 2) - (breite // 2)
        y = (win.winfo_screenheight() // 2) - (hoehe // 2)
        win.geometry("+%d+%d" % (x, y))

    mitte(popupfen)

    def name_fest(event = None):            # Name vom Input wird genutzt
        global spieler_name
        spieler_name = entry.get().strip()

        if not spieler_name: # Wenn kein Name gegeben wurde auf den Standard Namen zurückgreifen
            spieler_name = "Spieler"

        popupfen.destroy()  # Schließt das Fenster bei Namenseingabe

    popupfen.title("?")
    label = Label(popupfen, text=msg, font=NORM_FONT)
    label.pack(side="top", fill="x", pady=10)

    entry = Entry(popupfen, width=15)       # Namen Input
    entry.pack()
    entry.insert(0, "Spieler") #Standard Name
    entry.bind("<Return>", name_fest)
    entry.focus_set()

    button1 = Button(popupfen, text="Submit", command=name_fest)
    button1.pack()

    popupfen.mainloop()

def main():
    global start, game_over
    popup("Bitte Ihren Namen eingeben!")

    spieler.anzeigen(bildschirm)  # Schlange wird angezeigt
    apfel.anzeigen(bildschirm)      # Äpfel werden angezeigt
    waende_erstellen()      # Wände werden erstellt
    textausgabe()       # Wände werden angezeigt

    while sekunden > 0:
        countdown()     # Countdown vor dem Start 
        
    start = True

    while True:         # main loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if not game_over:
                    datei_erstellen()       # Ergebniss wird in Datei eingetragen
                
                pygame.quit()
                sys.exit()
                break

            elif event.type == pygame.KEYDOWN:      # Wenn eine Taste gedrückt wird verändert sich die Richtung der Schlange
                spieler.richtungsset(event.key)
            
            elif event.type == pygame.KEYUP:
                spieler.speed == 10

        
        bildschirm.fill(SCHWARZ)        # Bildschrim wird Schwarz
        waende_erstellen()
        textausgabe()
        spieler.anzeigen(bildschirm)
        apfel.anzeigen(bildschirm)

        if not game_over:
            spieler.bewegen() # solange nicht game over bewegt sich die Schlange

            if apfel_essen():
                spieler.punkte += apfel.groesse
                apfel.random_xy()
                Apfel.anzahl += 1  # Apfel count plus eins

            else:
                spieler.koerper.pop()  # letztes Körperteil der Schlange wird gelöscht beim Fortbewegen

        if spieler.gegen_wand(liste_waende): # checkt ob die SChlange kollidiert ist
            apfel.random_xy()
            if spieler.leben <= 0:
                game_over = True
                text_ausgeben(LARGE_FONT, "GAME OVER", ROT)
            
        uhr.tick(spieler.speed)

        pygame.display.flip() # Bildschirm wird updatet
        if game_over:
            datei_erstellen()  # ergebniss wird in die Datei geschrieben
            pygame.time.wait(2000)
            break

if __name__ == "__main__":
    main()

