from RULEngine.Strategy.Strategy import Strategy
from RULEngine.Framework import Framework
import sys, time

framework = Framework()

def start_game(main_loop):

    class DefiStrategy(Strategy):
        def __init__(self, field, referee, team, opponent_team, is_team_yellow=False):
            Strategy.__init__(self, field, referee, team, opponent_team)

            # Create InfoManager
            self.team.is_team_yellow = is_team_yellow

        def on_start(self):
            main_loop(self._send_command, self.field, self.referee, self.team, self.opponent_team)

        def on_halt(self):
            self.on_start()

        def on_stop(self):
            self.on_start()

    framework.start_game(DefiStrategy)
