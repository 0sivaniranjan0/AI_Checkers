# Pygame Checkers AI

A classic game of Checkers built with Pygame, where you can test your skills against two different AI opponents: a standard Minimax algorithm and a more optimized Alpha-Beta Pruning algorithm.

![Gameplay Screenshot](https://i.imgur.com/gK4f6gW.png)

*(You should replace the image link above with a GIF or screenshot of your own game running!)*

## Features

-   **Graphical User Interface**: Clean and simple UI built with Pygame.
-   **Two AI Modes**:
    -   **Minimax AI (Slower)**: A fundamental AI algorithm for turn-based games.
    -   **Alpha-Beta Pruning AI (Faster)**: An optimized version of Minimax that significantly speeds up decision-making.
-   **Valid Move Highlighting**: Click on a piece to see all possible moves highlighted in blue.
-   **Undo Functionality**: Made a mistake? Press the **'U'** key to undo your last move.
-   **Restart Game**: Press the **'R' key** to return to the main menu and start a new game.
-   **AI Performance Metrics**: The game displays how long the AI took to compute its move.

## Installation & Setup

To run this game on your local machine, follow these steps.

**1. Clone the repository:**

```bash
git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
cd your-repo-name
```

**2. Create a virtual environment (recommended):**

```bash
# For Windows
python -m venv venv
venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

**3. Install dependencies:**
The only dependency is Pygame. You can install it using the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

**4. Run the game:**

```bash
python runner.py
```

## How to Play

1.  Launch the game by running `runner.py`.
2.  From the main menu, select which AI you want to play against.
3.  You play as the **RED** pieces. The AI plays as the **WHITE** pieces.
4.  Click on one of your pieces to select it. Valid moves will be highlighted.
5.  Click on a highlighted blue circle to move your piece.
6.  Capture all the AI's pieces to win!

### Controls

-   **Mouse Click**: Select and move pieces.
-   **'U' Key**: Undo the previous move.
-   **'R' Key**: Restart the game and go back to the main menu.

## Project Structure

```
.
├── runner.py         # Main game loop, handles UI, menu, and events
├── checkers.py       # Contains all game logic: Board, Piece, AI algorithms
├── crown.png         # Image asset for king pieces
├── requirements.txt  # List of Python dependencies
└── README.md         # This file
```

## AI Implementation

The AI logic is located in `checkers.py`.

-   **`minimax()`**: This function implements the recursive Minimax algorithm. It explores the game tree to a certain depth to find the optimal move for the AI.
-   **`alphabeta()`**: This function implements Alpha-Beta Pruning. It is an optimization of Minimax that avoids evaluating branches of the game tree that are not relevant, making it much faster.
-   **`evaluate()`**: This is the heuristic function used by the AI to score the state of the board. The current evaluation is based on the number of remaining pieces and kings for each side.