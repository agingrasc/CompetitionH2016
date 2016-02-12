from util import Collision
from RULEngine.Util.Position import Position
# from util import raycast

COLLISION_ENV = None


def setup_module():
    """ Setup pour les fonctions """
    pos_list = [Position(0, 0), Position(100, 200), Position(-500, -300),
                Position(-433, -511)]
    # pylint: disable=W0603
    global COLLISION_ENV
    COLLISION_ENV = Collision(pos_list)


def test_detect():
    """ Est-ce qu'une collision est detecte? """
    assert COLLISION_ENV.raycast(Position(0, 0), None)


def test_position():
    """ Est-ce que la position de la collision est correcte? """
    assert COLLISION_ENV.raycast(Position(0, 0), None) == Position(100, 50)
