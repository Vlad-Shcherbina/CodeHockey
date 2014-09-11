from math import pi
import cmath
import copy


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


game = None

def register_game(game_, world):
    global game
    game = copy.deepcopy(game_)
    game.hockeyist_radius = world.hockeyists[0].radius
    game.puck_radius = world.puck.radius
    #game.radius

def get_game():
    return game
