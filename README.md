# Hand Gesture Controlled Game

This is a simple game that uses OpenCV and MediaPipe to track hand gestures and control game elements.

## Requirements

- Python 3.7+
- OpenCV
- MediaPipe
- Pygame
- Numpy

## Installation

Install the required packages:

```
pip install -r requirements.txt
```

## How to Play

1. Run the script:

   ```
   python main.py
   ```
2. Control the player with your hand gestures:
   Open palm: Move the player up
   Closed palm: Move the player down
3. Try to navigate through the obstacles to score points.
4. Press ESC to quit the game, or SPACE to restart after game over.

## Game Rules

- The player moves up when your palm is open and down when your palm is closed
- Each obstacle you pass gives you 1 point
- Colliding with an obstacle ends the game
- The game gets progressively more challenging as you score more points
