from RULEngine.Strategy.Strategy import Strategy
from RULEngine.Util.Pose import Strategy
from RULEngine.Util.Position import Strategy
from RULEngine.Framework import Framework
import sys, time

EVENT_SUCCEED = "success"
EVENT_TIMEOUT = "timeout"
EVENT_FAIL = "rate"
EVENT_WIP = "inprogress"

STATE_IDLE = "idle"
STATE_MOVING = "moving"

def getStrategy(main_loop):
    class DefiStrategy(Strategy):
            def __init__(self, field, referee, team, opponent_team, is_team_yellow=False):
                Strategy.__init__(self, field, referee, team, opponent_team)

                self.team.is_team_yellow = is_team_yellow

                self.robot_states = [STATE_IDLE for robot in team.robots]
                self.robot_events = [EVENT_SUCCEED for robot in team.robots]
                self.robot_goals = [Position() for robot in team.robots] #Position vide. Position visée
                self.robot_aim = [Position() for robot in team.robots] #Position vide. Position visée

            def on_start(self):
                main_loop(self, self.field, self.robot_event, self.team, self.opponent_team)

            def execute(self):
                for robot in robot_states:

            def on_halt(self):
                self.on_start()

            def on_stop(self):
                self.on_start()

            #----------Private---------

            def succeed(joueur):
                self.robot_events[joueur] = EVENT_SUCCEED
                self.robot_states[joueur] = STATE_IDLE

            def fail(joueur):
                self.robot_events[joueur] = EVENT_FAIL
                self.robot_states[joueur] = STATE_IDLE

            def timeout(joueur):
                self.robot_events[joueur] = EVENT_TIMEOUT
                self.robot_states[joueur] = STATE_IDLE

            def avancer(joueur):
                """MoveTo position desiree"""

            def idle(joueur):
                """MoveTo current position"""


            #----------Public----------
            def avancer(joueur, position):
                pass

def start_game(main_loop):

    framework = Framework()
    framework.start_game(DefiStrategy)
