from math import pi
import cmath
import copy
import logging


logger = logging.getLogger(__name__)


def complex_to_pair(z):
    return z.real, z.imag

def dot(z1, z2):
    return z1.real * z2.real + z1.imag * z2.imag


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


class CWorld(object):
    def __init__(self, world):
        self.tick = world.tick
        self.width = world.width
        self.height = world.height

        self.puck = CUnit(world.puck)
        self.all_hockeyists = sorted(
            map(CUnit, world.hockeyists),
            key=lambda h: h.unit.id)
        self.hockeyists = {1: [], 2: []}
        self.goalies = {}
        for h in self.all_hockeyists:
            if h.unit.type == 0:
                assert h.unit.player_id not in self.goalies
                self.goalies[h.unit.player_id] = h
            else:
                self.hockeyists[h.unit.player_id].append(h)

        self.players = sorted(world.players, key=lambda p: not p.me)
        self.score = ':'.join(str(p.goal_count) for p in self.players)


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


def predict_goalie(gy, puck_pos):
    r = game.hockeyist_radius
    d = puck_pos.imag - gy
    d = max(d, -game.goalie_max_speed)
    d = min(d, game.goalie_max_speed)
    gy += d
    gy = max(gy, game.goal_net_top + r)
    gy = min(gy, game.goal_net_top + game.goal_net_height - r)
    return gy


def trace_puck(pos, v, gy=None):
    """ Return pair (outcome, list of coords). """
    if gy is None:
        gy = pos.imag

    outcome = 0
    trace = []

    def check_hit(pos, v, gy):
        if pos.real > game.goal_net_width + game.puck_radius + game.hockeyist_radius * 2:
            return 0

        goalie_pos = complex(game.goal_net_width + game.hockeyist_radius, gy)
        if abs(goalie_pos - pos) < game.hockeyist_radius + game.puck_radius:
            return 1  # bounde

        if pos.real > game.goal_net_width + game.puck_radius:
            return 0

        if pos.real < game.goal_net_width:
            return 2  # goal

        if (pos.imag < game.goal_net_top or
            pos.imag > game.goal_net_top + game.goal_net_height):
            return 1  # bounce

        for c in goal_net_corners(1):
            n = pos - c
            if 1e-3 < abs(n) < game.puck_radius:
                n /= abs(n)
                v -= 2 * dot(n, v) * n
                if v.real < 0 or True:  # TODO
                    return 2  # goal
                else:
                    # TODO: coverage
                    return 1  # bounce

        return 0

    for i in range(100):
        pos += v
        v *= 0.999  # TODO: measure carefully
        trace.append(pos)
        h = check_hit(pos, v, gy)
        if h == 1:
            outcome = 0
            break
        elif h == 2:
            outcome = 1
            break
        h = check_hit(game.world_width - pos.conjugate(), -v.conjugate(), gy)
        if h == 1:
            outcome = 0
            break
        elif h == 2:
            outcome = 2
            break

        gy = predict_goalie(gy, pos)

    return outcome, trace


game = None

def register_game(game_, world):
    global game
    game = copy.deepcopy(game_)
    game.hockeyist_radius = world.hockeyists[0].radius
    game.puck_radius = world.puck.radius

    # TODO: wtf
    assert not hasattr(game, 'pass_power')
    game.pass_power = 20 * game.pass_power_factor
    assert not hasattr(game, 'base_strike_power')
    game.base_strike_power = 20 * game.strike_power_base_factor

def get_game():
    return game
