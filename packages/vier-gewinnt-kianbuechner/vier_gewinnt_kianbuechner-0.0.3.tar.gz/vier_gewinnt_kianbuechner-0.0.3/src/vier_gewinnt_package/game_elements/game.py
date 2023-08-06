import yaml

from src.vier_gewinnt_package.game_elements.game_table import GameTable
from src.vier_gewinnt_package.game_elements.player.type.ai import Ai
from src.vier_gewinnt_package.game_elements.player.type.human import Human


# Die Bestenliste wird aus dem YAML-File geladen, um dann sortiert und ausgegeben zu werden.
def print_leaderboard():
    with open(r"records.yaml") as file:
        records = yaml.full_load(file)

    # Die Datei wird zum ausgeben auf der Bestenliste, nach den Siegen gegen einen anderen menschlichen Spieler
    # sortiert.
    sorted_records = dict(sorted(records.items(), key=lambda x: x[1], reverse=True))

    # Formatierung, damit die Tabelle der Bestenliste korrekt angezeigt wird.
    player_string = "Spieler".ljust(10)
    vs_human_string = "vs. Mensch".ljust(10)
    vs_ai_string = "vs. Computer".ljust(10)

    leaderboard_string = f"\nBestenliste:\n{player_string} | {vs_human_string} | {vs_ai_string}\n" \
                         f"-------------------------------------- \n "

    for key in list(sorted_records.keys()):
        player_string = key.ljust(10)
        value_vs_human = str(sorted_records[key][0]).ljust(10)
        value_vs_ai = str(sorted_records[key][1]).ljust(10)
        leaderboard_string += f"{player_string} | {value_vs_human} | {value_vs_ai}\n"

    print(leaderboard_string)


class Game:
    def __init__(self):
        self.game_mode = None
        self.player_one = None
        self.player_two = None
        self.game_table = GameTable()

    def play_game(self):
        print_leaderboard()
        # Zu Beginn des Spiels kann der Spielmodus ausgewählt werden.
        self.game_mode = int(input(
            "Wähle einen Spielmodus 1 oder 2:\n 1 für PVP - Player Versus Player\n 2 für PVC - Player Versus Computer\n"
        ))
        if self.game_mode == 1:
            print("Du hast den PVP-Modus gewählt. Viel Spaß euch beiden!")
            self.player_one = Human(1)
            self.player_two = Human(2)
        elif self.game_mode == 2:
            print("Du hast den PVC-Modus gewählt. Viel Spaß gegen den Computer!")
            self.player_one = Human(1)
            self.player_two = Ai()

        # Die Variable is_game_over enthält ein Boolean der angibt, ob das Spiel vorbei ist.
        is_game_over = False
        self.game_table.print_game_table()

        # Solange is_game_over == False ist, wird die while-Schleife und somit das Spiel ausgeführt.
        while not is_game_over:
            is_game_over = self.game_table.find_and_exchange_lowest(self.player_one.player_move(),
                                                                    self.player_one, self.game_mode)
            if is_game_over:
                break
            is_game_over = self.game_table.find_and_exchange_lowest(self.player_two.player_move(),
                                                                    self.player_two, self.game_mode)
