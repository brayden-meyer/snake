import pygame
from enum import Enum
from pygame.math import *
import random
import SnakeGame
from Wall import Wall


class FruitType(Enum):
    APPLE = ("Apple", "res/fruit/apple.png")
    BANANA = ("Banana", "res/fruit/banana.png")
    PINEAPPLE = ("Pineapple", "res/fruit/pineapple.png")
    GRAPE = ("Grape", "res/fruit/grape.png")
    PUMPKIN = ("Pumpkin", "res/fruit/pumpkin.png")
    TURNIP = ("Turnip", "res/fruit/turnip.png")
    AUBERGINE = ("Aubergine", "res/fruit/aubergine.png")
    STRAWBERRY = ("Strawberry", "res/fruit/strawberry.png")
    CHERRY = ("Cherry", "res/fruit/cherry.png")
    CARROT = ("Carrot", "res/fruit/carrot.png")
    MUSHROOM = ("Mushroom", "res/fruit/mushroom.png")
    BROCCOLI = ("Broccoli", "res/fruit/broccoli.png")
    WATERMELON = ("Watermelon", "res/fruit/watermelon.png")

    def __init__(self, display_name, skin_path):
        self.display_name = display_name
        self.skin_path = skin_path


class PhantomFruitType(Enum):
    SALAD = ("Salad", "res/fruit/salad.png")
    WALL = ("Wall", "res/game_mode/wall.png")
    CHEESE = ("Cheese", "res/game_mode/cheese.png")
    ZEN = ("Zen", "res/game_mode/zen.png")

    def __init__(self, display_name, skin_path):
        self.display_name = display_name
        self.skin_path = skin_path


class Fruit(pygame.sprite.Sprite):
    """Represents a fruit on a game Board."""

    def __init__(self, type, board, row, column):
        super().__init__()
        self.board = board
        self.tile = self.board.get_tile(row, column)
        self.tile.fruit = self
        self.set_type(type)

    def set_type(self, type):
        if type is None:
            self.randomize_type()
            return
        self.type = type
        size = SnakeGame.Vector2I(Vector2(self.tile.rect.size).elementwise() * Vector2(1.5, 1.5))
        self.image = pygame.transform.scale(pygame.image.load(type.skin_path), size)
        tile_rect = self.tile.rect.copy()
        tile_width, tile_height = tile_rect.size
        image_width, image_height = self.image.get_size()
        self.rect = self.tile.rect.inflate(image_width - tile_width, image_height - tile_height)

    def set_tile(self, row, column):
        self.tile.fruit = None
        self.tile = self.board.get_tile(row, column)
        self.rect = self.tile.rect
        self.tile.fruit = self

    def randomize_tile(self):
        random_tile = self.board.get_random_tile()
        if isinstance(random_tile.wall, Wall):
            self.randomize_tile()
            return
        self.set_tile(random_tile.row, random_tile.column)

    def randomize_type(self):
        self.set_type(random.choice(list(FruitType)))


class PhantomFruit(Fruit):
    """Represents a "fruit" that is not part of the game. Used for changing game settings."""

    def __init__(self, type, board, row, column):
        pygame.sprite.Sprite.__init__(self)
        self.board = board
        self.tile = self.board.get_tile(row, column)
        self.tile.phantom_fruit = self
        self.set_type(type)

    def set_tile(self, row, column):
        self.tile.phantom_fruit = None
        self.tile = self.board.get_tile(row, column)
        self.rect = self.tile.rect
        self.tile.phantom_fruit = self

