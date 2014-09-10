from math import *
import logging

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


prev_tick = None


def move_to_target_controls(u, target):
    d = (target - u.pos) / u.dir
    if d.real > 0:
        speed_up = 1.0
    else:
        speed_up = 0
    if d.imag > 0:
        turn = 10
    else:
        turn = -10
    return speed_up, turn


class MyStrategy:
    def move(self, me: Hockeyist, world: World, game: Game, move: Move):
        global prev_tick
        if world.tick != prev_tick:
            prev_tick = world.tick
            if recorder:
                recorder.tick(world.tick, world, game)

            if world.tick == 0:
                register_game(game)
                logging.info(game.stick_sector)
            logging.info(repr(world.tick))

        me = CUnit(me)
        puck = CUnit(world.puck)

        move.speed_up, move.turn = move_to_target_controls(me, puck.pos)

        move.action = ActionType.TAKE_PUCK

        if me.inside_sector(puck.pos):
            logging.info('strike')
            move.action = ActionType.STRIKE
