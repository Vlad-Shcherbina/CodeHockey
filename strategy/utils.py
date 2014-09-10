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
        if abs(d) > game.stick_length or abs(d) < 1e-6:
            return False
        return abs(cmath.phase(d)) < game.stick_sector * 0.5


def goal_net_corners(player_id):
    if player_id == 1:
        x = game.goal_net_width
        return (
            complex(x, game.goal_net_top + game.goal_net_height),
            complex(x, game.goal_net_top))
    elif player_id == 2:
        x = game.world_width - game.goal_net_width
        return (
            complex(x, game.goal_net_top),
            complex(x, game.goal_net_top + game.goal_net_height))
    else:
        assert False, player_id


game = None

def register_game(game_):
    global game
    game = game_
