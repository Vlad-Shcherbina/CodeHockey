from math import *
import logging
import copy

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


class MoveInstruction:
    pass


def every_tick(world):
    logging.info(repr(world.tick))

    puck = world.puck

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

    moves = {}
    for me in world.hockeyists[world.player_id]:
        move = MoveInstruction()
        move.speed_up, move.turn = move_to_target_controls(me, puck.pos)

        move.action = ActionType.TAKE_PUCK

        if me.inside_sector(puck.pos):
            d = puck.pos - me.pos
            corners = goal_net_corners(me.unit.player_id)
            ds = [(c - puck.pos) / d for c in corners]
            if ds[0].imag < 0 and ds[1].imag > 0:
                if me.unit.remaining_cooldown_ticks == 0:
                    logging.info('strike!')
                    move.action = ActionType.STRIKE
                else:
                    logging.info('waiting to strike')
                    move.action = ActionType.STRIKE
            else:
                if puck.unit.owner_hockeyist_id == me.unit.id:
                    if ds[1].imag > 0:
                        logging.info('aiming right')
                        move.turn = 10
                    elif ds[1].imag < 0:
                        logging.info('aiming left')
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
            if cworld.tick == 0:
                register_game(game, world)

            if recorder:
                log_draw = recorder.tick(cworld.tick, cworld, game)

            moves = every_tick(cworld)
            prev_world = copy.deepcopy(cworld)

        if moves is not None and me.id in moves:
            for k, v in moves[me.id].__dict__.items():
                setattr(move, k, v)
