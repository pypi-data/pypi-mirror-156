from src.vier_gewinnt_package.game_elements.player.player import Player


class Human(Player):
    def __init__(self, num):
        super().__init__(num)
        self.set_name()

    # Vom menschlichen Spieler wird ein Input gefordert um einen Spielzug zu machen.
    def player_move(self):
        column = None
        is_valid_input = False
        while not is_valid_input:

            # Mit einem try-catch wird der Fall, dass der Benutzer keinen Input eingibt, abgedeckt.
            try:
                column = int(
                    input(f"{self.name}, gib die Nummer 1-5 der Spalte an, in die du deinen Spielstein setzen möchtest:"
                          ))
                if column in range(1, 6):
                    is_valid_input = True
                else:
                    print("Deine Eingabe ist kein Zahl zwischen 1 und 5, versuche es nochmal!")
            except ValueError:
                print("Deine Eingabe ist ungültig, versuche es nochmal!")

        return column - 1

    # Der Name des menschlichen Spielers wird abgefragt und als Attribut abgespeichert.
    def set_name(self):
        self.name = input(f"Spieler {self.num}, gib deinen Namen ein: ")
