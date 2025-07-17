import pygame

pygame.init()

# Game window settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GAME_WINDOW = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Hand Gesture Game")
SCORE_FONT = pygame.font.SysFont('Arial', 30)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Game settings
FPS = 60
PLAYER_SIZE = 50
OBSTACLE_WIDTH = 50
OBSTACLE_GAP = 200
OBSTACLE_SPEED = 5
GRAVITY = 1
JUMP_STRENGTH = -15