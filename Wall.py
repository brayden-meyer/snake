import pygame
from pygame.math import *
import random


class Wall(pygame.sprite.Sprite):
    """Represents a Wall on a game Board."""

    def __init__(self, board, row, column):
        super().__init__()
        self.board = board
        self.tile = self.board.get_tile(row, column)
        self.tile.wall = self
        self.rect = self.tile.rect
        surface = pygame.surface.Surface(self.rect.size)
        surface.fill(board.wall_color)
        self.image = surface

