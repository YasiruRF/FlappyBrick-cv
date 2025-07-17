import pygame
import random
from settings import *

class Player:
    def __init__(self):
        self.x = WINDOW_WIDTH // 4
        self.y = WINDOW_HEIGHT // 2
        self.velocity = 0
        self.img = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.img.fill(BLUE)
        self.rect = pygame.Rect(self.x, self.y, PLAYER_SIZE, PLAYER_SIZE)
    
    def update(self, l_shape, index_finger_up):
        # Move player based on hand gesture
        if l_shape:
            self.velocity = 0  # Stable flight
        else:
            if index_finger_up:
                self.velocity = JUMP_STRENGTH  # Move up when index finger is up
            else:
                self.velocity = abs(JUMP_STRENGTH)  # Move down when index finger is down
        
        self.y += self.velocity
        
        # Keep player within game window
        if self.y < 0:
            self.y = 0
        if self.y > WINDOW_HEIGHT - PLAYER_SIZE:
            self.y = WINDOW_HEIGHT - PLAYER_SIZE
        
        self.rect = pygame.Rect(self.x, self.y, PLAYER_SIZE, PLAYER_SIZE)
    
    def draw(self, surface):
        surface.blit(self.img, (self.x, self.y))

class Obstacle:
    def __init__(self, x):
        self.x = x
        self.gap_y = random.randint(OBSTACLE_GAP, WINDOW_HEIGHT - OBSTACLE_GAP)
        self.gap_height = OBSTACLE_GAP
        self.top_height = self.gap_y - self.gap_height // 2
        self.bottom_height = WINDOW_HEIGHT - self.top_height - self.gap_height
        self.top_rect = pygame.Rect(self.x, 0, OBSTACLE_WIDTH, self.top_height)
        self.bottom_rect = pygame.Rect(
            self.x, WINDOW_HEIGHT - self.bottom_height, 
            OBSTACLE_WIDTH, self.bottom_height
        )
        self.passed = False
    
    def update(self):
        self.x -= OBSTACLE_SPEED
        self.top_rect.x = self.x
        self.bottom_rect.x = self.x
    
    def draw(self, surface):
        pygame.draw.rect(surface, GREEN, self.top_rect)
        pygame.draw.rect(surface, GREEN, self.bottom_rect)