""" Expose une classe Collision qui garde les etats interne et implemente les
fonctionnalite pour detecter des collisions. """


import logging
from RULEngine.Util.constant import ROBOT_RADIUS
from RULEngine.Util.geometry import get_distance
from RULEngine.Util.Position import Position
from RULEngine.Util.Pose import Pose
from RULEngine.Game.Player import Player
logging.basicConfig(filename='debug.log', level=logging.DEBUG,
                    format='%(asctime)s %(message)s')


class Collision:
    """ Conserve les positions des objets sur le terrain. """

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

    def check_collision(self):
        """ Interface public ..."""
        self._is_collision()

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

    def raycast(self, pos, vec):
        """ Execute un tracage de rayon de la position dans la direction du
        vecteur. Retourne une position s'il y a collision, autrement retourne
        None """
        if isinstance(pos, Position):
            raise TypeError("pos doit etre une Position")

        if isinstance(vec, None):
            raise TypeError("vec doit etre un Vecteur")
        return None

    def _collision(self, pos, pos2=None, max_distance=ROBOT_RADIUS):
        """ Logique pour la collision. """
        logging.info('Number of object to check: %d', len(self.field_objects))
        if pos2 is None:
            for i in self.field_objects:
                obj_pos = i
                distance = get_distance(pos, obj_pos)
                logging.info('Distance is %d', distance)
                if distance < 2*max_distance:
                    return True
            return False
        else:
            distance = get_distance(pos, pos2)
            return distance < 2*max_distance

    def _is_collision(self):
        """ Verifie si un objet dans la liste est en collision, retourne la liste
        des tuples des Position en collision """
        logging.info('Checking for collisions')
        ret = []
        l_objs = self.field_objects
        for i in self.field_objects:
            for j in l_objs:
                if self._collision(i, j):
                    ret.append((i, j))
        return ret
