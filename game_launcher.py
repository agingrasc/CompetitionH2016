from RULEngine.Strategy.Strategy import Strategy
from RULEngine.Util.Pose import Pose
from RULEngine.Util.Position import Position
from RULEngine.Util import geometry
from RULEngine.Game.Player import Player
from RULEngine.Game.Ball import Ball
from RULEngine.Command import Command
from RULEngine.Framework import Framework
import math as m

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
                self.robot_kick_force = [0 for robot in team.players] #Force de kick
                self.robot_kick_times = [0 for robot in team.players] #Nombre de kick

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

            def checkedNextStep(self, state, joueur):
                if self.robot_events[joueur] == EVENT_SUCCEED:
                    self.robot_events[joueur] = EVENT_WIP
                    self.robot_states[joueur] = state


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

            def _getDeadZone(self, posType):
                if isinstance(posType, Player):
                    return 225
                elif isinstance(posType, Ball):
                    return 225
                elif isinstance(posType, Position):
                    return 50

            def _bouger(self, joueur):
                #TODO: ajuster la deadzone en fonction du type du goal
                position = self._convertirPosition(self.robot_goals[joueur])
                player = self.team.players[joueur]
                dist = geometry.get_distance(player.pose.position, position)
                deadzone = self._getDeadZone(self.robot_goals[joueur])

                if dist < deadzone: # si la distance est exactement 0, la position n'est pas bonne
                    self._succeed(joueur)
                else:
                    orientation = player.pose.orientation
                    command = Command.MoveToAndRotate(player, self.team,
                                                      Pose(position, orientation))
                    self._send_command(command)

            def _bougerPlusAim(self, joueur, deadzone=None):
                destination = self._convertirPosition(self.robot_goals[joueur])
                cible = self._convertirPosition(self.robot_aim[joueur])
                if not deadzone:
                    deadzone = self._getDeadZone(self.robot_goals[joueur])
                player = self.team.players[joueur]
                dist = geometry.get_distance(player.pose.position, destination)
                angle = m.fabs(geometry.get_angle(player.pose.position, cible) - player.pose.orientation)  #angle between the robot and the ball

                if(dist <= deadzone and angle <= 0.09):  #0.087 rad = 5 deg : marge d'erreur de l'orientation
                    self._succeed(joueur)
                elif(dist > deadzone and angle <= 0.09):
                    command = Command.MoveTo(player, self.team, destination)
                    self._send_command(command)
                elif(dist <= deadzone and angle > 0.09):
                    orientation = geometry.get_angle(player.pose.position, cible)
                    command = Command.Rotate(player, self.team, orientation)
                    self._send_command(command)
                else:
                    orientation = geometry.get_angle(player.pose.position, cible)
                    command = Command.MoveToAndRotate(player, self.team, Pose(destination, orientation))
                    self._send_command(command)

            def _lancer(self, joueur):
                self.robot_goals[joueur] = self._lance_position(joueur)
                self._bougerPlusAim(joueur)
                self.robot_kick_times[joueur] = 100
                self.checkedNextStep(self._lancer_p2, joueur)

            def _lancer_p2(self, joueur):
                self.robot_goals[joueur] = self.field.ball
                player = self.team.players[joueur]
                if self.robot_kick_times[joueur] > 0:
                    command = Command.Kick(player, self.team, 8)
                    self._send_command(command)
                    self.robot_kick_times[joueur] -= 1
                else:
                    self._succeed(joueur)

            def _lance_position(self, joueur):
                player = self.team.players[joueur]
                robot = self._convertirPosition(player)
                balle = self._convertirPosition(self.field.ball)
                cible = self._convertirPosition(self.robot_aim[joueur])
                dist = geometry.get_distance(robot, balle)
                lim_dist = dist*0.5
                deadzone = lim_dist if lim_dist > 125 else 60
                angle = m.fabs(geometry.get_angle(robot, cible) - player.pose.orientation)
                if angle > 0.3:
                    deadzone = max(deadzone, 200)

                print(deadzone)

                angle = m.atan2(robot.y-cible.y,
                                robot.x-cible.x)
                x = balle.x + deadzone*m.cos(angle)
                y = balle.y + deadzone*m.sin(angle)
                return Position(x, y)

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
                    self.robot_aim[joueur] = cible
                    self.robot_states[joueur] = self._bougerPlusAim
                else:
                    self.robot_states[joueur] = self._bouger
                self.robot_events[joueur] = EVENT_WIP

            def passe(self, joueur1, joueur2):
                self._fail(joueur1)
                self._fail(joueur2)

            def lancer(self, joueur, cible, force=5):
                self.robot_kick_force[joueur] = force
                position = self._lance_position(joueur)
                self.bouger(joueur, position, cible=cible)
                self.robot_states[joueur] = self._lancer
                self.robot_events[joueur] = EVENT_WIP

            def chercher_balle(self, joueur):
                ballPosition = self.field.ball
                self.bouger(joueur, ballPosition, cible=self.field.ball)

            def positioner_entre_deux_ennemis(self, joueur, enemi1, enemi2):
                self._fail(joueur)

    return DefiStrategy


def start_game(main_loop):

    framework = Framework()
    framework.start_game(getStrategy(main_loop))
