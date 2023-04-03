import pygame
from pygame.locals import *
from pygame.math import *
from enum import Enum, auto
from Board import Board, BoardSize
from Fruit import Fruit, FruitType, PhantomFruit, PhantomFruitType
from Snake import Snake


class PlayMode(Enum):
    CLASSIC = auto()
    WALL = auto()
    ZEN = auto()
    CHEESE = auto()


class OptionMode(Enum):
    CHANGE_FRUIT = auto()
    CHANGE_GAME_MODE = auto()
    CHANGE_SPEED = auto()
    CHANGE_SNAKE = auto()


class GameMode:
    def __init__(self, play_mode, option_mode=None):
        self.play_mode = play_mode
        self.option_mode = option_mode


class SnakeGame:
    SIZE = Vector2(544, 480)
    ORIGIN = SIZE / 2
    FPS = 100
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()

        # Initialize display.
        pygame.display.set_caption("Snake")
        pygame.display.set_icon(pygame.image.load("res/icon.png"))
        self.screen = pygame.display.set_mode(Vector2I(SnakeGame.SIZE))

        # Initialize font.
        self.font = pygame.font.Font("res/font/bit5x5.ttf", 24)

        # Initialize sounds.
        self.eat_sound = pygame.mixer.Sound('res/sound/eat.wav')
        self.up_sound = pygame.mixer.Sound('res/sound/up.ogg')
        self.down_sound = pygame.mixer.Sound('res/sound/down.ogg')
        self.left_sound = pygame.mixer.Sound('res/sound/left.ogg')
        self.right_sound = pygame.mixer.Sound('res/sound/right.ogg')
        self.death_sound = pygame.mixer.Sound('res/sound/death.ogg')

        # Initialize sprites.
        self.game_mode = GameMode(PlayMode.CLASSIC)
        self.fruit_type = FruitType.APPLE
        self.sprites = pygame.sprite.Group()
        self.fruits = pygame.sprite.Group()
        self.board = Board(BoardSize.MEDIUM, pygame.Rect(0, 0, *SnakeGame.SIZE))
        self.fruit = Fruit(FruitType.APPLE, self.board, 7, 12)
        self.fruits.add(self.fruit)
        self.sprites.add(self.board)
        self.snake = Snake(self.board, self)
        self.snake.body = [Vector2(7, 3), Vector2(7, 2), Vector2(7, 1)]

        self.fruit_options = {
            PhantomFruit(FruitType.APPLE, self.board, 7, 1): FruitType.APPLE,
            PhantomFruit(FruitType.BANANA, self.board, 3, 2): FruitType.BANANA,
            PhantomFruit(FruitType.PINEAPPLE, self.board, 3, 4): FruitType.PINEAPPLE,
            PhantomFruit(FruitType.GRAPE, self.board, 3, 6): FruitType.GRAPE,
            PhantomFruit(FruitType.PUMPKIN, self.board, 3, 8): FruitType.PUMPKIN,
            PhantomFruit(FruitType.TURNIP, self.board, 3, 10): FruitType.TURNIP,
            PhantomFruit(FruitType.AUBERGINE, self.board, 3, 12): FruitType.AUBERGINE,
            PhantomFruit(FruitType.STRAWBERRY, self.board, 3, 14): FruitType.STRAWBERRY,
            PhantomFruit(FruitType.CHERRY, self.board, 11, 3): FruitType.CHERRY,
            PhantomFruit(FruitType.CARROT, self.board, 11, 5): FruitType.CARROT,
            PhantomFruit(FruitType.MUSHROOM, self.board, 11, 7): FruitType.MUSHROOM,
            PhantomFruit(FruitType.BROCCOLI, self.board, 11, 9): FruitType.BROCCOLI,
            PhantomFruit(FruitType.WATERMELON, self.board, 11, 11): FruitType.WATERMELON,
            PhantomFruit(PhantomFruitType.SALAD, self.board, 11, 13): None
        }
        self.fruit_options_sprites = pygame.sprite.Group(*self.fruit_options)
        self.game_mode_options = {
            PhantomFruit(FruitType.APPLE, self.board, 7, 1): PlayMode.CLASSIC,
            PhantomFruit(PhantomFruitType.WALL, self.board, 3, 5): PlayMode.WALL,
            PhantomFruit(PhantomFruitType.ZEN, self.board, 3, 11): PlayMode.ZEN,
            PhantomFruit(PhantomFruitType.CHEESE, self.board, 11, 5): PlayMode.CHEESE
        }
        self.game_mode_options_sprites = pygame.sprite.Group(*self.game_mode_options)

        # Create a custom Pygame event for snake movement: 1 grid square = 100 ms
        SnakeGame.SCREEN_UPDATE = pygame.USEREVENT
        pygame.time.set_timer(SnakeGame.SCREEN_UPDATE, 100)

        # Define controls by key, snake movement and sound. Arrow keys will move the snake.
        self.controls = {
            K_UP: (Snake.up, self.up_sound),
            K_DOWN: (Snake.down, self.down_sound),
            K_LEFT: (Snake.left, self.left_sound),
            K_RIGHT: (Snake.right, self.right_sound)
        }

        self.playing = True
        self.score = 0
        self.high_score = 0
        hud_text_score = {
            OptionMode.CHANGE_FRUIT: 'Change Fruit',
            OptionMode.CHANGE_GAME_MODE: 'Change Game Mode'
        }
        while self.playing:
            # Handle events.
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.playing = False
                elif event.type == SnakeGame.SCREEN_UPDATE:
                    if self.snake.move_snake():
                        # Snake is alive, check if it ate.
                        if self.game_mode.option_mode is not None and self.snake.phantom_eat():
                            phantom_fruit = self.snake.get_head_tile().phantom_fruit
                            if self.game_mode.option_mode == OptionMode.CHANGE_FRUIT and phantom_fruit in self.fruit_options:
                                self.eat_sound.play()
                                self.fruit_type = self.fruit_options[phantom_fruit]
                                self.fruit.set_type(self.fruit_type)
                                self.game_mode.option_mode = None
                            elif self.game_mode.option_mode == OptionMode.CHANGE_GAME_MODE and phantom_fruit in self.game_mode_options:
                                self.eat_sound.play()
                                self.game_mode.play_mode = self.game_mode_options[phantom_fruit]
                                self.game_mode.option_mode = None
                        elif self.game_mode.option_mode is None and self.snake.eat():
                            self.eat_sound.play()
                            self.score += 1
                            self.fruit.set_type(self.fruit_type)
                            # Create a wall if the new score if odd (and play mode is WALL)
                            if self.score % 2 != 0 and self.game_mode.play_mode == PlayMode.WALL:
                                self.board.create_random_wall()
                    else:
                        # Snake died.
                        self.death_sound.play()
                        # Reset snake.
                        self.snake = Snake(self.board, self)
                        self.snake.body = [Vector2(7, 3), Vector2(7, 2), Vector2(7, 1)]
                        # Reset fruit.
                        self.fruit.set_tile(7, 12)
                        self.fruit.set_type(self.fruit_type)
                        # Set high score and reset score.
                        self.high_score = self.score if self.score > self.high_score else self.high_score
                        self.score = 0
                        # Clear dynamic walls.
                        for wall in self.board.dynamic_walls:
                            wall.tile.wall = None
                            wall.kill()
                elif event.type == KEYDOWN:
                    # Handle key presses.
                    if event.key in self.controls:
                        snake_moved = self.controls.get(event.key)[0](self.snake)
                        # Only play move sound if the snake successfully moved.
                        if snake_moved:
                            self.controls.get(event.key)[1].play()
                    elif event.key in (K_f, K_g):
                        # Reset snake.
                        self.snake = Snake(self.board, self)
                        self.snake.body = [Vector2(7, 9), Vector2(7, 8), Vector2(7, 7)]
                        # Reset fruit.
                        self.fruit.set_tile(7, 12)
                        self.fruit.set_type(self.fruit_type)
                        # Set high score and reset score.
                        # Set high score and reset score.
                        self.high_score = self.score if self.score > self.high_score else self.high_score
                        self.score = 0
                        # Clear dynamic walls.
                        for wall in self.board.dynamic_walls:
                            wall.tile.wall = None
                            wall.kill()
                        if event.key == K_f:
                            self.game_mode.option_mode = OptionMode.CHANGE_FRUIT
                            for phantom_fruit in self.fruit_options:
                                phantom_fruit.tile.phantom_fruit = phantom_fruit
                        elif event.key == K_g:
                            self.game_mode.option_mode = OptionMode.CHANGE_GAME_MODE
                            for phantom_fruit in self.game_mode_options:
                                phantom_fruit.tile.phantom_fruit = phantom_fruit

            # Draw sprites and snake.
            self.screen.fill(Board.LIGHT_GREEN)
            self.sprites.draw(self.screen)
            self.board.static_walls.draw(self.screen)
            self.board.dynamic_walls.draw(self.screen)

            if self.game_mode.option_mode is not None:
                if self.game_mode.option_mode == OptionMode.CHANGE_FRUIT:
                    self.fruit_options_sprites.draw(self.screen)
                elif self.game_mode.option_mode == OptionMode.CHANGE_GAME_MODE:
                    self.game_mode_options_sprites.draw(self.screen)
            else:
                if self.game_mode.play_mode in (PlayMode.CLASSIC, PlayMode.WALL, PlayMode.ZEN, PlayMode.CHEESE):
                    self.fruits.draw(self.screen)

            self.snake.draw_snake(self.screen)

            # Draw score.
            score_text = self.font.render(hud_text_score.get(self.game_mode.option_mode, str(self.score)), True, SnakeGame.BLACK)
            score_text_center = self.board.get_tile(1, 8).rect.center
            self.screen.blit(score_text, center_on_point(score_text_center, score_text.get_size()))

            # Draw high score.
            if self.high_score > 0:
                high_score_text = self.font.render(str(self.high_score) if self.game_mode.option_mode is None else '', True, SnakeGame.WHITE)
                high_score_text_center = self.board.get_tile(2, 8).rect.center
                self.screen.blit(high_score_text, center_on_point(high_score_text_center, high_score_text.get_size()))

            pygame.display.flip()
            self.clock.tick(SnakeGame.FPS)


# Utility functions
def Vector2I(vector):
    """Convert Pygame Vector2 (storing floats) to a tuple of integers."""
    return round(vector[0]), round(vector[1])


def center_on_point(point, size):
    x, y = point
    width, height = size
    return x - width/2, y - height/2

