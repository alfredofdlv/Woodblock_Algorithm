# Woody Block Search Algorithms

This project implements various search algorithms to solve problems in the game **Woody Block**. It includes both uninformed (blind) and informed (heuristic-based) search techniques, allowing users to compare their performance and effectiveness.

## Project Files

- `algorithms.py`  
  Contains common functions and classes used by the different search strategies.

- `blind_search.py`  
  Implementation of uninformed (blind) search algorithms.

- `informed_search.py`  
  Implementation of informed search algorithms using heuristics.

- `main.py`  
  The main script that runs the search algorithms on the Woody Block game.

- `requirements.txt`  
  Lists all dependencies required to run the project.

- `simulation.py`  
  Simulates the Woody Block game environment and defines the initial problem states.


## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/alfredofdlv/Solitaire_Game.git
   cd Solitaire_Game

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt

## Usage

To run the project:

    python main.py

This will start the Woody Block game simulation and apply the implemented search algorithms to find solutions.

## Project Overview

The goal of this project is to explore and compare different search strategies in solving puzzles within the **Woody Block** game environment.

Implemented algorithms include:

- **Blind Search:**  
  Methods implemented:
  - BFS
  - DFS
  - IDS
  - UCS  

- **Informed Search:**  
  Methods implemented:
  - Greedy Search
  - A* Search
  - Weighted A*  

The core logic shared across algorithms is implemented in `algorithms.py`.

## Requirements

- Python 3.7 or higher
- Dependencies listed in `requirements.txt`

## Notes

- You can edit the simulation file to test different game scenarios or customize the environment.

---

Developed as a class project to implement and experiment with search algorithms in a game-based setting.
