# Das verrückte Labyrinth :)




Pygame Oberfläche: 
- Startmenü: 
    * Einstellungen 
    * Hosten 
    * Joinen 
    * Tutorial
    * Quit 
    
- Host: 
    * Code automatisch generieren beim Knopf drücken 
    * Spieler in der Lobby Übersicht
    * Spiel starten Knopf
    
- Join: 
    * Textfeld zum Namen eingeben 
    * Textfeld zum Code eingeben 
    * Dann weiterleiten auf Queue

- Lobby (nur für Joined Spieler)
    * Übersicht über alle Spieler 
    * Lobby verlassen 
    
---

Spiel startet: 
- Server generiert Spielfeld und Zielkarten + Startspieler, schickt es an alle Spieler
- HUD rechts neben dem Brett: 
    * Aktuelle Karte, die man einsetzen darf mit Pfeilen zum drehen. Dann auf gelben Pfeil am Spielfeld drücken zum Reinschieben
    * Für den Spieler aktuell aufgedeckte Symbolkarte
    * Liste mit Spielern und aufgedeckten Symbolen 
- Man hat Knopf zum Aufgeben => Dann Zuschauermodus 
- Wenn man im Zuschauermodus ist kann man Spiel verlassen 
- Wenn Host verlässt wird neuer Host gewählt
- Wenn Spiel vorbei geht wieder in die Lobby um neues Spiel zu starten 
    
- Wenn Spielfigur rausgeschoben wird, wird Spieler auf das neue Feld auf der anderen Seite geschoben 
- Mehrere Figuren auf dem gleichen Feld möglich 



Weitere Features: 
- Timeout bzw. Zuguhr 