import pygame
from enum import Enum
import random
from Wall import Wall
from Fruit import Fruit


class BoardSize(Enum):
    SMALL = (17, 15)
    MEDIUM = (17, 15)
    LARGE = (17, 15)

    def __init__(self, columns, rows):
        self.columns = columns
        self.rows = rows


class Tile:
    """Represents a singular tile on the Board."""
    def __init__(self, rect, board, row, column):
        self.rect = rect
        self.board = board
        self.row = row
        self.column = column
        self.fruit = None
        self.phantom_fruit = None
        self.wall = None


class Board(pygame.sprite.Sprite):
    """Represents the array-backed grid of tiles a Snake can move on or a Fruit can be placed on."""
    LIGHT_GREEN = (175, 215, 70)
    DARK_GREEN = (167, 209, 61)
    wall_color = (77, 127, 46)

    def __init__(self, size, rect):
        super().__init__()
        self.rect = rect
        self.image = self.tile(size)
        self.static_walls = pygame.sprite.Group()
        self.dynamic_walls = pygame.sprite.Group()

    def tile(self, size):
        """Generates an array-backed grid for the Board, given a BoardSize, with alternating grass colors."""
        self.size = size
        # Generate placeholder values for the array backing the grid.
        self.tiles = [[None for _ in range(self.size.columns)] for _ in range(self.size.rows)]

        surface = pygame.surface.Surface(self.rect.size)
        surface.fill(Board.LIGHT_GREEN)

        # Calculate width and height of tiles to fill the BoardSize.
        tile_width = self.rect.width / self.size.columns
        tile_height = self.rect.height / self.size.rows

        for row in range(self.size.rows):
            if row % 2 == 0:
                # Iterate over columns in even rows.
                for column in range(self.size.columns):
                    tile_rect = pygame.Rect(column * tile_width, row * tile_height, tile_width, tile_height)
                    self.tiles[row][column] = Tile(tile_rect, self, row, column)
                    # Only color even-column tiles in even rows.
                    if column % 2 == 0:
                        pygame.draw.rect(surface, Board.DARK_GREEN, tile_rect)
            else:
                # Iterate over columns in odd rows.
                for column in range(self.size.columns):
                    tile_rect = pygame.Rect(column * tile_width, row * tile_height, tile_width, tile_height)
                    self.tiles[row][column] = Tile(tile_rect, self, row, column)
                    # Only color odd-column tiles in odd rows.
                    if column % 2 != 0:
                        pygame.draw.rect(surface, Board.DARK_GREEN, tile_rect)

        return surface

    def get_tile(self, row, column):
        """Returns the tile [row][column] on the game Board where row, column < the BoardType size."""
        return self.tiles[int(row)][int(column)]

    def get_random_tile(self):
        """Returns a random tile on the game Board."""
        return self.get_tile(random.randrange(self.size.rows), random.randrange(self.size.columns))

    def create_wall(self, row, column, static=False):
        """Create a Wall at the specified row and column; return the Wall."""
        wall = Wall(self, row, column)
        self.get_tile(row, column).wall = wall
        wall_group = self.static_walls if static else self.dynamic_walls
        wall_group.add(wall)
        return wall

    def create_random_wall(self, static=False):
        """Create a Wall at a random tile; return the Wall."""
        tile = self.get_random_tile()
        if isinstance(tile.wall, Wall) or isinstance(tile.fruit, Fruit):
            self.create_random_wall()
            return
        return self.create_wall(tile.row, tile.column)

