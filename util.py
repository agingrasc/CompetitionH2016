from RULEngine.Util.constant import ROBOT_RADIUS
from RULEngine.Util.geometry import get_distance
from RULEngine.Util.Position import Position
from RULEngine.Util.Pose import Pose
from RULEngine.Game.Player import Player
import logging
logging.basicConfig(filename='debug.log', level=logging.DEBUG, format='%(asctime)s %(message)s')


class Collision:

    def __init__(self, objs):
        if isinstance(objs[0], Position):
            self.field_objects = objs
            logging.info('Receive position list')
        elif isinstance(objs[0], Pose):
            self.field_objects = []
            for i in objs:
                self.field_objects.append(i.position)
        elif isinstance(objs[0], Player):
            self.field_objects = []
            for i in objs:
                self.field_objects.append(i.pose.position)

    def collision(self, pos):
        """ Retourne True si la position ou les positions projete provoque une
        collision. Envoyer la position actuelle du robot retourne True """
        if isinstance(pos, list):
            for i in pos:
                if self._collision(i):
                    return True
            return False
        else:
            return self._collision(pos)

    def _collision(self, pos):
        logging.info('Number of object to check: %d', len(self.field_objects))
        for i in self.field_objects:
            obj_pos = i
            distance = get_distance(pos, obj_pos)
            logging.info('Distance is %d', distance)
            if distance < 2*ROBOT_RADIUS:
                return True
        return False
