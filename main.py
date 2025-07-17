import cv2
from cvzone.HandTrackingModule import HandDetector
import pygame
import sys
from settings import *
from objects import Player, Obstacle

# Initialize Pygame
pygame.init()

# Initialize Hand Detector
detector = HandDetector(staticMode=False, maxHands=1, modelComplexity=1, detectionCon=0.5, minTrackCon=0.5)

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
    l_shape = False
    index_finger_up = False
    v_shape = False

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
                    # Reset game (keyboard fallback)
                    game_active = True
                    player = Player()
                    obstacles = [Obstacle(WINDOW_WIDTH + i * 300) for i in range(3)]
                    score = 0

        # Process webcam frame
        success, frame = cap.read()
        if not success:
            print("Error: Could not read frame from webcam")
            break

        frame = cv2.flip(frame, 1)  # Mirror effect

        # Find hands
        hands, frame = detector.findHands(frame)

        if hands:
            hand = hands[0]
            fingers = detector.fingersUp(hand)

            # Detect L shape: Thumb and index up
            l_shape = fingers == [1, 1, 0, 0, 0]

            # Detect V shape: Index and middle up
            v_shape = fingers == [0, 1, 1, 0, 0]

            index_finger_up = fingers[1] == 1
        else:
            l_shape = False
            index_finger_up = False
            v_shape = False

        # Restart game with V-shape
        if not game_active and v_shape:
            game_active = True
            player = Player()
            obstacles = [Obstacle(WINDOW_WIDTH + i * 300) for i in range(3)]
            score = 0
            pygame.time.delay(500)  # Prevent multiple restarts from one gesture

        # Display hand status on webcam
        if l_shape:
            status_text = "L-Shape Detected"
        elif v_shape:
            status_text = "V-Shape Detected (Restart)"
        else:
            status_text = "Up" if index_finger_up else "Down"

        cv2.putText(
            frame, f"Status: {status_text}", (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2
        )

        cv2.imshow("Hand Tracking", frame)

        # Game logic
        if game_active:
            player.update(l_shape, index_finger_up)

            if obstacles[-1].x < WINDOW_WIDTH - 300:
                obstacles.append(Obstacle(WINDOW_WIDTH))

            for obstacle in obstacles:
                obstacle.update()

                if not obstacle.passed and obstacle.x + OBSTACLE_WIDTH < player.x:
                    obstacle.passed = True
                    score += 1

            obstacles = [obs for obs in obstacles if obs.x + OBSTACLE_WIDTH > 0]

            if check_collision(player, obstacles):
                game_active = False

            # Draw game
            GAME_WINDOW.fill(BLACK)
            player.draw(GAME_WINDOW)
            for obstacle in obstacles:
                obstacle.draw(GAME_WINDOW)

            score_text = SCORE_FONT.render(f"Score: {score}", True, WHITE)
            GAME_WINDOW.blit(score_text, (10, 10))

        else:
            GAME_WINDOW.fill(BLACK)
            game_over_text = SCORE_FONT.render("Game Over", True, RED)
            score_text = SCORE_FONT.render(f"Final Score: {score}", True, WHITE)
            restart_text = SCORE_FONT.render("V-Sign to Restart or Press SPACE", True, WHITE)

            GAME_WINDOW.blit(game_over_text, (WINDOW_WIDTH // 2 - game_over_text.get_width() // 2, WINDOW_HEIGHT // 2 - 60))
            GAME_WINDOW.blit(score_text, (WINDOW_WIDTH // 2 - score_text.get_width() // 2, WINDOW_HEIGHT // 2))
            GAME_WINDOW.blit(restart_text, (WINDOW_WIDTH // 2 - restart_text.get_width() // 2, WINDOW_HEIGHT // 2 + 60))

        pygame.display.update()
        clock.tick(FPS)

        if cv2.waitKey(1) & 0xFF == 27:  # ESC key
            break

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()

if __name__ == "__main__":
    main()
