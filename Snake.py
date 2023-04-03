import pygame
from pygame.math import *
from Fruit import Fruit, PhantomFruit
from Wall import Wall
import SnakeGame


class Snake(pygame.sprite.Sprite):
    DIRECTION_UP = Vector2(-1, 0)
    DIRECTION_DOWN = Vector2(1, 0)
    DIRECTION_LEFT = Vector2(0, -1)
    DIRECTION_RIGHT = Vector2(0, 1)
    AXIS_VERTICAL = (DIRECTION_UP, DIRECTION_DOWN)
    AXIS_HORIZONTAL = (DIRECTION_LEFT, DIRECTION_RIGHT)

    def __init__(self, board, game):
        super().__init__()
        # Load head images.
        self.head_up = pygame.image.load('res/snake/head_up.png').convert_alpha()
        self.head_down = pygame.image.load('res/snake/head_down.png').convert_alpha()
        self.head_right = pygame.image.load('res/snake/head_right.png').convert_alpha()
        self.head_left = pygame.image.load('res/snake/head_left.png').convert_alpha()

        # Load tail images.
        self.tail_up = pygame.image.load('res/snake/tail_up.png').convert_alpha()
        self.tail_down = pygame.image.load('res/snake/tail_down.png').convert_alpha()
        self.tail_right = pygame.image.load('res/snake/tail_right.png').convert_alpha()
        self.tail_left = pygame.image.load('res/snake/tail_left.png').convert_alpha()

        # Load body images.
        self.body_vertical = pygame.image.load('res/snake/body_vertical.png').convert_alpha()
        self.body_horizontal = pygame.image.load('res/snake/body_horizontal.png').convert_alpha()
        self.body_tr = pygame.image.load('res/snake/body_tr.png').convert_alpha()
        self.body_tl = pygame.image.load('res/snake/body_tl.png').convert_alpha()
        self.body_br = pygame.image.load('res/snake/body_br.png').convert_alpha()
        self.body_bl = pygame.image.load('res/snake/body_bl.png').convert_alpha()

        self.board = board
        self.game = game
        # Set defaults.
        self.body = []
        self.new_block = False
        self.direction = Vector2(0, 0)
        self.head = self.head_right
        self.tail = self.tail_right
        self.body_graphic = self.body_horizontal

    def draw_snake(self, screen):
        cheese = self.game.game_mode.play_mode == SnakeGame.PlayMode.CHEESE
        for index, block in enumerate(self.body):
            tile_rect = self.board.get_tile(*block).rect.copy()

            # Select the appropriate head image.
            heads = {
                (1, 0): self.head_up,
                (-1, 0): self.head_down,
                (0, 1): self.head_left,
                (0, -1): self.head_right
            }
            # Look up head vector - adjacent body vector in the dictionary.
            self.head = heads.get(tuple(self.body[1] - self.body[0]), self.head_right)

            # Select the appropriate tail image.
            tails = {
                (1, 0): self.tail_up,
                (-1, 0): self.tail_down,
                (0, 1): self.tail_left,
                (0, -1): self.tail_right
            }
            # Look up tail vector - adjacent body vector in the dictionary.
            self.tail = tails.get(tuple(self.body[-2] - self.body[-1]), self.head_right)

            if index == 0:
                # Draw head.
                screen.blit(self.head, tile_rect)
            elif index == len(self.body) - 1:
                # Draw tail.
                screen.blit(self.tail, tile_rect)
            else:
                if cheese and index % 2 != 0:
                    continue
                # Select appropriate body image.
                previous_block = self.body[index + 1] - block
                next_block = self.body[index - 1] - block
                # Travelling straight
                if previous_block.x == next_block.x:  # Vertical
                    self.body_graphic = self.body_horizontal
                elif previous_block.y == next_block.y:  # Horizontal
                    self.body_graphic = self.body_vertical
                else:
                    # Turning a corner
                    # Down to left/right to up
                    if previous_block.x == -1 and next_block.y == -1 or previous_block.y == -1 and next_block.x == -1:
                        self.body_graphic = self.body_tl
                    # Down to right/left to up
                    elif previous_block.x == -1 and next_block.y == 1 or previous_block.y == 1 and next_block.x == -1:
                        self.body_graphic = self.body_tr
                    # Up to left/right to down
                    elif previous_block.x == 1 and next_block.y == -1 or previous_block.y == -1 and next_block.x == 1:
                        self.body_graphic = self.body_bl
                    # Up to right/left to down
                    elif previous_block.x == 1 and next_block.y == 1 or previous_block.y == 1 and next_block.x == 1:
                        self.body_graphic = self.body_br
                # Draw body.
                screen.blit(self.body_graphic, tile_rect)

    def move_snake(self):
        """Moves the Snake. Returns True if the move was successful; False if the Snake hit itself or the wall."""
        zen = self.game.game_mode.play_mode == SnakeGame.PlayMode.ZEN
        cheese = self.game.game_mode.play_mode == SnakeGame.PlayMode.CHEESE
        option = self.game.game_mode.option_mode is not None

        if self.direction == (0, 0):
            return True

        if self.new_block:
            body_copy = self.body[:]
            self.new_block = False
        else:
            body_copy = self.body[:-1]

        new_head = body_copy[0] + self.direction

        # Check if the Snake hits itself.
        if new_head in body_copy and not zen and not option:
            if cheese and body_copy.index(new_head) % 2 != 0:
                pass
            else:
                return False

        # Check if the Snake moves outside of the grid.
        if new_head.x not in range(self.board.size.rows) or new_head.y not in range(self.board.size.columns):
            return False

        # Check if the Snake hits a wall.
        if not zen and not option and isinstance(self.board.get_tile(new_head.x, new_head.y).wall, Wall):
            return False

        body_copy.insert(0, new_head)
        self.body = body_copy[:]

        return True

    def eat(self):
        """Attempts to eat any Fruit at the Tile of the Snake head. Returns True if the Snake eats; False if it does not."""
        head_tile = self.board.get_tile(*self.body[0])
        fruit = head_tile.fruit
        if isinstance(fruit, Fruit):
            fruit.randomize_tile()
            self.new_block = True
            return True
        return False

    def phantom_eat(self):
        head_tile = self.board.get_tile(*self.body[0])
        phantom_fruit = head_tile.phantom_fruit
        if type(phantom_fruit) == PhantomFruit:
            return True
        return False

    def get_head_tile(self):
        return self.board.get_tile(*self.body[0])

    def up(self):
        """Changes the Snake's direction to up (if it was not already traveling in the vertical axis). Returns True if successful."""
        if self.direction not in Snake.AXIS_VERTICAL or self.game.game_mode.play_mode == SnakeGame.PlayMode.ZEN or self.game.game_mode.option_mode is not None:
            self.direction = Snake.DIRECTION_UP
            return True
        return False

    def down(self):
        """Changes the Snake's direction to down (if it was not already traveling in the vertical axis). Returns True if successful."""
        if self.direction not in Snake.AXIS_VERTICAL or self.game.game_mode.play_mode == SnakeGame.PlayMode.ZEN or self.game.game_mode.option_mode is not None:
            self.direction = Snake.DIRECTION_DOWN
            return True
        return False

    def left(self):
        """Changes the Snake's direction to left (if it was not already traveling in the horizontal axis). Returns True if successful."""
        if self.direction not in Snake.AXIS_HORIZONTAL or self.game.game_mode.play_mode == SnakeGame.PlayMode.ZEN or self.game.game_mode.option_mode is not None:
            self.direction = Snake.DIRECTION_LEFT
            return True
        return False

    def right(self):
        """Changes the Snake's direction to right (if it was not already traveling in the horizontal axis). Returns True if successful."""
        if self.direction not in Snake.AXIS_HORIZONTAL or self.game.game_mode.play_mode == SnakeGame.PlayMode.ZEN or self.game.game_mode.option_mode is not None:
            self.direction = Snake.DIRECTION_RIGHT
            return True
        return False

    def add_block(self):
        """Add a new body block to the Snake on the next move_snake() call."""
        self.new_block = True

