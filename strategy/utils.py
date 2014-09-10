from math import pi
import cmath


def complex_to_pair(z):
    return z.real, z.imag


class CUnit(object):
    def __init__(self, unit):
        self.pos = complex(unit.x, unit.y)
        self.dir = cmath.rect(1, unit.angle)
        self.v = complex(unit.speed_x, unit.speed_y)
        self.angle = unit.angle
        self.angular_speed = unit.angular_speed

        self.radius = unit.radius
        self.mass = unit.mass

        self.unit = unit

    def inside_sector(self, pos):
        d = (pos - self.pos) / self.dir
        if abs(d) > game.stick_length:
            return False
        return abs(cmath.phase(d)) < game.stick_sector * 0.5


game = None

def register_game(game_):
    global game
    game = game_
