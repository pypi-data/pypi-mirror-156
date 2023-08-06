import random

from src.vier_gewinnt_package.game_elements.player.player import Player


class Ai(Player):
    def __init__(self):
        super().__init__(2)
        self.name = "Computer"

    # Der Computer macht immer einen zufälligen Spielzug.
    def player_move(self):
        return random.randint(0, 4)
