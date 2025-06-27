import cv2
import mediapipe as mp
import numpy as np
import pygame
import random
import sys
import time

# Initialize Pygame
pygame.init()

# Game window settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GAME_WINDOW = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Hand Gesture Game")

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
SCORE_FONT = pygame.font.SysFont('Arial', 30)

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

class Player:
    def __init__(self):
        self.x = WINDOW_WIDTH // 4
        self.y = WINDOW_HEIGHT // 2
        self.velocity = 0
        self.img = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.img.fill(BLUE)
        self.rect = pygame.Rect(self.x, self.y, PLAYER_SIZE, PLAYER_SIZE)
    
    def update(self, index_finger_up):
        # Move player based on hand gesture
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
    
    def draw(self):
        GAME_WINDOW.blit(self.img, (self.x, self.y))

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
    
    def draw(self):
        pygame.draw.rect(GAME_WINDOW, GREEN, self.top_rect)
        pygame.draw.rect(GAME_WINDOW, GREEN, self.bottom_rect)

def is_index_finger_up(hand_landmarks):
    if not hand_landmarks:
        return False
    
    # Get index finger landmarks
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    index_pip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP]
    index_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]
    
    # Check if index finger is extended upward
    # In camera coordinates, smaller y value means higher position
    finger_extended = index_tip.y < index_pip.y < index_mcp.y
    
    return finger_extended

def check_collision(player, obstacles):
    for obstacle in obstacles:
        if player.rect.colliderect(obstacle.top_rect) or player.rect.colliderect(obstacle.bottom_rect):
            return True
    return False

def main():
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return
    
    clock = pygame.time.Clock()
    player = Player()
    obstacles = [Obstacle(WINDOW_WIDTH + i * 300) for i in range(3)]
    score = 0
    game_active = True
    index_finger_up = False
    
    # Main game loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                cap.release()
                cv2.destroyAllWindows()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_active:
                    # Reset game
                    game_active = True
                    player = Player()
                    obstacles = [Obstacle(WINDOW_WIDTH + i * 300) for i in range(3)]
                    score = 0
        
        # Process webcam frame
        success, frame = cap.read()
        if not success:
            print("Error: Could not read frame from webcam")
            break
        
        # Flip horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Convert to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process with MediaPipe
        results = hands.process(rgb_frame)
        
        # Determine if index finger is up or down
        if results.multi_hand_landmarks:
            index_finger_up = is_index_finger_up(results.multi_hand_landmarks[0])
            
            # Draw hand landmarks
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style()
                )
        
        # Display hand status
        status_text = "Up" if index_finger_up else "Down"
        cv2.putText(
            frame, f"Index Finger: {status_text}", (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2
        )
        
        # Show webcam view
        cv2.imshow("Hand Tracking", frame)
        
        # Game logic
        if game_active:
            # Update game elements
            player.update(index_finger_up)
            
            # Add new obstacle when needed
            if obstacles[-1].x < WINDOW_WIDTH - 300:
                obstacles.append(Obstacle(WINDOW_WIDTH))
            
            # Update obstacles
            for obstacle in obstacles:
                obstacle.update()
                
                # Score when passing an obstacle
                if not obstacle.passed and obstacle.x + OBSTACLE_WIDTH < player.x:
                    obstacle.passed = True
                    score += 1
            
            # Remove off-screen obstacles
            obstacles = [obs for obs in obstacles if obs.x + OBSTACLE_WIDTH > 0]
            
            # Check for collisions
            if check_collision(player, obstacles):
                game_active = False
            
            # Draw game elements
            GAME_WINDOW.fill(BLACK)
            player.draw()
            for obstacle in obstacles:
                obstacle.draw()
            
            # Draw score
            score_text = SCORE_FONT.render(f"Score: {score}", True, WHITE)
            GAME_WINDOW.blit(score_text, (10, 10))
        else:
            # Game over screen
            GAME_WINDOW.fill(BLACK)
            game_over_text = SCORE_FONT.render("Game Over", True, RED)
            score_text = SCORE_FONT.render(f"Final Score: {score}", True, WHITE)
            restart_text = SCORE_FONT.render("Press SPACE to restart", True, WHITE)
            
            GAME_WINDOW.blit(game_over_text, (WINDOW_WIDTH // 2 - game_over_text.get_width() // 2, WINDOW_HEIGHT // 2 - 60))
            GAME_WINDOW.blit(score_text, (WINDOW_WIDTH // 2 - score_text.get_width() // 2, WINDOW_HEIGHT // 2))
            GAME_WINDOW.blit(restart_text, (WINDOW_WIDTH // 2 - restart_text.get_width() // 2, WINDOW_HEIGHT // 2 + 60))
        
        pygame.display.update()
        clock.tick(FPS)
        
        if cv2.waitKey(1) & 0xFF == 27:  # ESC to exit
            break
    
    # Clean up
    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()

if __name__ == "__main__":
    main()

