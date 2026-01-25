"""
Module __init__ cho algorithms package
"""

from .maze_generator import MazeGenerator
from .bfs import BFS
from .dijkstra import Dijkstra
from .astar import AStar

__all__ = ['MazeGenerator', 'BFS', 'Dijkstra', 'AStar']
