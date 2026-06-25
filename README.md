# 🧩 AI 8 & 15-Puzzle Solver & 2D Pathfinding Visualizer

A professional, full-stack Python desktop application designed to visualize how artificial intelligence solves complex problems. This project features two main modules: a classic 8 & 15-Puzzle solver (3X3 and 4X4 grids) and a 2D Grid Pathfinding engine that navigates from a start point to a goal while avoiding obstacles. 

🚀 Key Features

* **2D Obstacle Pathfinding:** An interactive 2D grid where the AI must find the optimal route from a Start node to a Goal node while safely navigating around user-defined obstacles.
* **8 & 15-Puzzle Engine:** Watch the AI solve the 8-puzzle and 15-puzzle games in real-time.
* **Mathematical Solvability Pre-Check:** For the N-Puzzle, the system instantly calculates inversion parity to determine if a board is solvable before wasting CPU resources.
* **Interactive GUI Visualizer:** Built entirely in Tkinter, featuring a step-by-step playback system with adjustable speeds.
* **Live Code Tracking:** A synchronized pseudo-code tracker highlights exactly which line of algorithm logic is executing at any given millisecond.
* **Benchmarking Dashboard:** Compare two different algorithms side-by-side to analyze execution time (ms), total visited nodes, and optimal path length.

## 🧠 Implemented Algorithms

The application visualizes how different graph-search paradigms explore state spaces and 2D environments:

**Uninformed Search (No Heuristics):**
* Depth-First Search (DFS)
* Breadth-First Search (BFS)
* Uniform Cost Search (UCS)

**Informed Search (Heuristic-Based):**
* A* Search (A-Star)
* Iterative Deepening A* (IDA*)

**Heuristics Used:**
* **Hamming Distance:** Counts the number of misplaced elements.
* **Manhattan Distance:** Calculates the total grid distance an element is from its goal using the formula: 
  D = sum |x - x{goal}| + |y - y{goal}|

## ⚙️ Installation & Usage

1. Clone the repository to your local machine:
   ```bash
   git clone [https://github.com/YourUsername/AI-Pathfinding-NPuzzle.git](https://github.com/YourUsername/AI-Pathfinding-NPuzzle.git)

2. Navigate to the project directory:
   ```bash
   cd Puzzle solver AI Project

3. Run the main application (requires Python 3.x):
   ```bash
   py solver.py
(Note: You can also run python SolverExplain.py to view the pseudo-code tracking interface).