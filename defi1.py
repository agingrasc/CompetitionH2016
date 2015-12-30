#!/usr/bin/python
import game_launcher
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Game.Player import Player

class Defi1(object):

    a = 0
    def boucle_principale(self, coach, terrain, etats, equipe_bleu, equipe_jaune):
        if self.a == 0:
            self.a = 1
            coach.bouger(0, terrain.ball)



defi = Defi1()
game_launcher.start_game(defi.boucle_principale)


