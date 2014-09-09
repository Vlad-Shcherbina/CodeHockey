from math import *

from model.ActionType import ActionType
from model.Game import Game
from model.Move import Move
from model.Hockeyist import Hockeyist
from model.World import World

try:
    import recorder
except ImportError:
    recorder = None


prev_tick = None


class MyStrategy:
    def move(self, me: Hockeyist, world: World, game: Game, move: Move):
        global prev_tick
        if world.tick != prev_tick:
            prev_tick = world.tick
            if recorder:
                recorder.tick(world.tick, world, game)

        move.speed_up = -1.0
        move.turn = pi
        move.action = ActionType.STRIKE
