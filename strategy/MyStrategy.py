from math import *
import logging
import copy
import random

from model.ActionType import ActionType
from model.Game import Game
from model.Move import Move
from model.Hockeyist import Hockeyist
from model.World import World

from utils import *

try:
    import recorder
except ImportError:
    recorder = None


prev_world = None


def move_to_target_controls(u, target):
    d = (target - u.pos) / u.dir
    if d.real > 0:
        speed_up = 1.0
    else:
        speed_up = 0
    turn = 0
    if d.imag > 1:
        turn = 10
    if d.imag < -1:
        turn = -10
    return speed_up, turn


def draw_trace(outcome, trace):
    for p in trace:
        log_draw.circle(p, 2, outline=(255, 255, 255, 80))
    color = {0: (128, 128, 128, 128), 1: (255, 0, 0, 128), 2: (0, 0, 255, 128)}
    log_draw.circle(p, 6, fill=color[outcome])


def draw_hit_locations():
    logging.info('pass power %s', get_game().pass_power)
    x0 = int(get_game().goal_net_width + get_game().puck_radius + 2)
    hz = True
    for x in range(x0, int(get_game().world_width) - x0, 50):
        for y in range(0, int(get_game().world_height), 50):
            for a in range(0, 180, 3):
                dir = cmath.rect(1, (a / 180 + 0.5) * pi)
                pos = complex(x, y)
                #v = dir * get_game().pass_power * 2
                v = 20 * dir
                #log_draw.circle(pos, 2, outline=(255, 255, 255, 128))
                if trace_puck(pos, v)[0] == 1:
                    if hz:
                        draw_trace(*trace_puck(pos, v))
                        hz = False
                    log_draw.line(pos, pos + 20 * dir, fill=(255, 255, 255, 200))


class MoveInstruction:
    pass


def every_tick(world):
    logging.info(repr(world.tick))

    puck = world.puck
    if world.tick % 20 == 0:
        logging.info('score %s', world.score)
    #logging.info('puck speed: %s', abs(puck.v))

    if prev_world:
        if prev_world.puck.unit.owner_hockeyist_id != world.puck.unit.owner_hockeyist_id:
            logging.info('puck changed owner to %s', world.puck.unit.owner_player_id)

    if world.goalies:
        gy = world.goalies[1].unit.y
        world.predicted_gy = predict_goalie(gy, puck.pos)

        if prev_world:
            gy = world.goalies[1].unit.y
            if abs(prev_world.predicted_gy - gy) > 1e-3:
                logging.warning('predicted_gy={}, gy={}'.format(
                    prev_world.predicted_gy, gy))

    if log_draw:
        log_draw.circle(puck.pos, puck.radius, outline=(255, 255, 255, 80))
        # if world.tick % 10 == 0:
        #     draw_trace(*trace_puck(puck.pos, puck.v))
        if world.tick == 0:
            draw_hit_locations()

    moves = {}
    for me in world.hockeyists[world.player_id]:
        move = MoveInstruction()
        move.speed_up, move.turn = move_to_target_controls(me, puck.pos)

        move.action = ActionType.TAKE_PUCK

        if me.inside_sector(puck.pos):
            d = puck.pos - me.pos
            d /= abs(d)
            corners = goal_net_corners(me.unit.player_id)
            ds = [(c - puck.pos) / d for c in corners]
            if ds[0].imag < 0 and ds[1].imag > 0:
                if me.unit.remaining_cooldown_ticks == 0:
                    strike_v = get_game().base_strike_power + dot(me.dir, me.v)
                    strike_v *= me.dir
                    outcome, trace = trace_puck(puck.pos, strike_v)
                    if log_draw:
                        draw_trace(outcome, trace)
                    if outcome == me.unit.player_id or random.randrange(5) == 0 or world.tick > 5995:
                        logging.info('strike!')
                        move.action = ActionType.STRIKE
                    else:
                        logging.info('aiming')
                        move.turn = 10 - 20 * (world.tick // 6 % 2)
                else:
                    logging.info('waiting to strike')
            else:
                if puck.unit.owner_hockeyist_id == me.unit.id:
                    if ds[1].imag > 0:
                        #logging.info('aiming right')
                        move.turn = 10
                    elif ds[1].imag < 0:
                        #logging.info('aiming left')
                        move.turn = -10
        moves[me.unit.id] = move

    return moves


moves = None
log_draw = None

class MyStrategy:
    def move(self, me: Hockeyist, world: World, game: Game, move: Move):
        global prev_world, moves, log_draw
        if prev_world is None or world.tick != prev_world.tick:
            cworld = CWorld(world)
            cworld.player_id = me.player_id
            random.seed(42)
            if cworld.tick == 0:
                register_game(game, world)

            if recorder:
                log_draw = recorder.tick(cworld.tick, cworld, game)

            moves = every_tick(cworld)
            prev_world = copy.deepcopy(cworld)

        if moves is not None and me.id in moves:
            for k, v in moves[me.id].__dict__.items():
                setattr(move, k, v)
