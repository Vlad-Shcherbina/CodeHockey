from math import *
from model.ActionType import ActionType
from model.Game import Game
from model.Move import Move
from model.Hockeyist import Hockeyist
from model.World import World


class MyStrategy:
    def move(self, me: Hockeyist, world: World, game: Game, move: Move):
        move.speed_up = -1.0
        move.turn = pi
        move.action = ActionType.STRIKE
