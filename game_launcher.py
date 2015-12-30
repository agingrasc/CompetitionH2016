from RULEngine.Strategy.Strategy import Strategy
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Util import geometry
from RULEngine.Game.Player import Player
from RULEngine.Game.Ball import Ball
from RULEngine.Command import Command
from RULEngine.Framework import Framework

import sys, time

EVENT_SUCCEED = "success"
EVENT_TIMEOUT = "timeout"
EVENT_FAIL = "rate"
EVENT_WIP = "inprogress"

def getStrategy(main_loop):
    class DefiStrategy(Strategy):
            def __init__(self, field, referee, team, opponent_team, is_team_yellow=False):
                Strategy.__init__(self, field, referee, team, opponent_team)

                self.team.is_team_yellow = is_team_yellow

                self.robot_states = [self._idle for robot in team.players]
                self.robot_events = [EVENT_SUCCEED for robot in team.players]
                self.robot_goals = [Position() for robot in team.players] #Position vide. Position visée
                self.robot_aim = [Position() for robot in team.players] #Position vide. Position visée

            def on_start(self):
                main_loop(self, self.field, self.robot_events, self.team, self.opponent_team)
                self.execute()

            def execute(self):
                for index, state in enumerate(self.robot_states):
                    state(index)

            def on_halt(self):
                self.on_start()

            def on_stop(self):
                self.on_start()

            def _convertirPosition(self, position):
                if isinstance(position, Player):
                    return position.pose.position
                elif isinstance(position, Ball):
                    return position.position
                elif isinstance(position, Position):
                    return position


            # ----------Private---------

            def _succeed(self, joueur):
                self.robot_events[joueur] = EVENT_SUCCEED
                self.robot_states[joueur] = self._idle

            def _fail(self, joueur):
                self.robot_events[joueur] = EVENT_FAIL
                self.robot_states[joueur] = self._idle

            def _timeout(self, joueur):
                self.robot_events[joueur] = EVENT_TIMEOUT
                self.robot_states[joueur] = self._idle

            def _bouger(self, joueur):
                position = self._convertirPosition(self.robot_goals[joueur])

                player = self.team.players[joueur]
                dist = geometry.get_distance(player.pose.position, position)
                print(dist)
                if 0 < dist < 150: # si la distance est exactement 0, la position n'est pas bonne
                    self._succeed(joueur)
                else:
                    orientation = player.pose.orientation
                    command = Command.MoveToAndRotate(player, self.team,
                                                      Pose(position, orientation))
                    self._send_command(command)

            def _bougerPlusAim(self, joueur):
                #TODO
                position = self._convertirPosition(self.robot_goals[joueur])

                player = self.team.players[joueur]
                dist = geometry.get_distance(player.pose.position, position)
                if 0 < dist < 100: # si la distance est exactement 0, la position n'est pas bonne
                    self._succeed(joueur)
                else:
                    orientation = player.pose.orientation
                    command = Command.MoveToAndRotate(player, self.team,
                                                      Pose(position, orientation))
                    self._send_command(command)

            def _idle(self, joueur):
                player = self.team.players[joueur]
                pose = player.pose
                command = Command.MoveToAndRotate(player, self.team, pose)
                self._send_command(command)

            # ----------Public----------
            def bouger(self, joueur, position, cible=None):
                assert(isinstance(joueur, int))
                assert(isinstance(position, (Position, Player, Ball, int)))
                self.robot_goals[joueur] = position
                if cible:
                    self.robot_goals[joueur] = cible
                    self.robot_states[joueur] = self._bougerPlusAim
                else:
                    self.robot_states[joueur] = self._bouger

            def passe(self, joueur1, joueur2):
                self._fail(joueur1)
                self._fail(joueur2)

            def lancer(self, joueur, cible, force=1):
                self._fail(joueur)

            def chercher_balle(self, joueur):
                self._fail(joueur)

            def positioner_entre_deux_ennemis(self, joueur, enemi1, enemi2):
                self._fail(joueur)

    return DefiStrategy


def start_game(main_loop):

    framework = Framework()
    framework.start_game(getStrategy(main_loop))
