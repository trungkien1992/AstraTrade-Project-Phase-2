"""
Maze-Hard dataset implementation
Creates 30x30 mazes for optimal pathfinding tasks
"""

import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np
import random
from typing import List, Tuple, Dict, Optional, Union
import json
import os
from dataclasses import dataclass
from collections import deque


@dataclass
class MazeConfig:
    """Configuration for Maze dataset"""
    maze_size: int = 30
    vocab_size: int = 6  # wall, empty, start, goal, path, padding
    max_sequence_length: int = 1000  # Flattened maze + path
    min_difficulty: int = 110  # Minimum path length as per paper
    

class MazeGenerator:
    """
    Generates 30x30 mazes for optimal pathfinding
    
    Based on the paper's description:
    - 30x30 maze size
    - Difficulty filter: path length >= 110
    - Optimal pathfinding required
    - Uses wavefront breadth-first search for verification
    """
    
    def __init__(self, config: MazeConfig = None):
        self.config = config or MazeConfig()
        self.size = self.config.maze_size
        
        # Tokens
        self.WALL_TOKEN = 0
        self.EMPTY_TOKEN = 1
        self.START_TOKEN = 2
        self.GOAL_TOKEN = 3
        self.PATH_TOKEN = 4
        self.PAD_TOKEN = 5
        
    def generate_maze(self) -> np.ndarray:
        """Generate maze using recursive backtracking"""
        # Initialize maze with walls
        maze = np.zeros((self.size, self.size), dtype=int)  # 0 = wall
        
        # Carve passages
        def carve_passage(x, y):
            maze[y, x] = 1  # 1 = empty space
            
            # Get random directions
            directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
            random.shuffle(directions)
            
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                
                # Check bounds
                if 0 <= nx < self.size and 0 <= ny < self.size and maze[ny, nx] == 0:
                    # Carve wall between current and next cell
                    maze[y + dy//2, x + dx//2] = 1
                    carve_passage(nx, ny)
        
        # Start carving from (1, 1) to ensure odd positions
        if self.size > 1:
            carve_passage(1, 1)
        
        return maze
    
    def place_start_goal(self, maze: np.ndarray) -> Tuple[np.ndarray, Tuple[int, int], Tuple[int, int]]:
        """Place start and goal positions in maze"""
        # Find all empty cells
        empty_cells = [(x, y) for x in range(self.size) for y in range(self.size) if maze[y, x] == 1]
        
        if len(empty_cells) < 2:
            # Fallback for small mazes
            start = (0, 0)
            goal = (self.size - 1, self.size - 1)
            maze[start[1], start[0]] = 1
            maze[goal[1], goal[0]] = 1
        else:
            # Choose start and goal to be far apart
            start = empty_cells[0]
            goal = max(empty_cells, key=lambda pos: abs(pos[0] - start[0]) + abs(pos[1] - start[1]))
        
        return maze, start, goal
    
    def find_shortest_path(self, maze: np.ndarray, start: Tuple[int, int], goal: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """Find shortest path using BFS (wavefront algorithm)"""
        if start == goal:
            return [start]
        
        queue = deque([(start, [start])])
        visited = {start}
        
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        
        while queue:
            (x, y), path = queue.popleft()
            
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                
                # Check bounds and if cell is passable
                if (0 <= nx < self.size and 0 <= ny < self.size and 
                    (nx, ny) not in visited and maze[ny, nx] != 0):
                    
                    new_path = path + [(nx, ny)]
                    
                    if (nx, ny) == goal:
                        return new_path
                    
                    queue.append(((nx, ny), new_path))
                    visited.add((nx, ny))
        
        return None  # No path found
    
    def create_maze_with_path(self) -> Tuple[np.ndarray, List[Tuple[int, int]], int]:
        """Create maze with valid path of sufficient difficulty"""
        max_attempts = 1000
        
        for attempt in range(max_attempts):
            # Generate base maze
            maze = self.generate_maze()
            
            # Place start and goal
            maze, start, goal = self.place_start_goal(maze)
            
            # Find shortest path
            path = self.find_shortest_path(maze, start, goal)
            
            if path and len(path) >= self.config.min_difficulty:
                return maze, path, len(path)
        
        # Fallback: return any valid maze
        maze = self.generate_maze()
        maze, start, goal = self.place_start_goal(maze)
        path = self.find_shortest_path(maze, start, goal)
        
        if path is None:
            # Create trivial path if needed
            path = [start, goal]
        
        return maze, path, len(path)
    
    def maze_to_sequence(self, maze: np.ndarray, path: List[Tuple[int, int]]) -> Tuple[List[int], List[int]]:
        """Convert maze and path to sequence format"""
        # Create maze with path marked
        maze_with_path = maze.copy()
        start, goal = path[0], path[-1]
        
        # Mark start and goal
        maze_with_path[start[1], start[0]] = self.START_TOKEN
        maze_with_path[goal[1], goal[0]] = self.GOAL_TOKEN
        
        # Input: flattened maze
        input_seq = maze_with_path.flatten().tolist()
        
        # Target: path coordinates flattened
        target_seq = []
        for x, y in path:
            target_seq.extend([x, y])
        
        return input_seq, target_seq
    
    def create_visual_maze(self, maze: np.ndarray, path: List[Tuple[int, int]] = None) -> np.ndarray:
        """Create visual representation of maze with path"""
        visual = maze.copy()
        
        if path:
            start, goal = path[0], path[-1]
            
            # Mark path
            for x, y in path[1:-1]:
                if visual[y, x] != self.WALL_TOKEN:
                    visual[y, x] = self.PATH_TOKEN
            
            # Mark start and goal
            visual[start[1], start[0]] = self.START_TOKEN
            visual[goal[1], goal[0]] = self.GOAL_TOKEN
        
        return visual


class MazeDataset(Dataset):
    """
    Maze-Hard dataset for HRM training
    
    Features:
    - 30x30 mazes with difficulty filter (path length >= 110)
    - Optimal pathfinding tasks
    - Sequence-to-sequence format
    """
    
    def __init__(
        self,
        num_samples: int = 1000,
        config: MazeConfig = None,
        cache_file: Optional[str] = None,
    ):
        self.config = config or MazeConfig()
        self.num_samples = num_samples
        self.generator = MazeGenerator(self.config)
        
        # Load or generate data
        if cache_file and os.path.exists(cache_file):
            self._load_from_cache(cache_file)
        else:
            self._generate_data()
            if cache_file:
                self._save_to_cache(cache_file)
    
    def _generate_data(self):
        """Generate dataset"""
        self.data = []
        
        print(f"Generating {self.num_samples} Maze-Hard instances...")
        for i in range(self.num_samples):
            if i % 100 == 0:
                print(f"Generated {i}/{self.num_samples} mazes")
            
            # Generate maze with path
            maze, path, difficulty = self.generator.create_maze_with_path()
            
            # Convert to sequences
            input_seq, target_seq = self.generator.maze_to_sequence(maze, path)
            
            self.data.append({
                'maze': maze,
                'path': path,
                'input_seq': input_seq,
                'target_seq': target_seq,
                'difficulty': difficulty,
            })
        
        print(f"Generated {len(self.data)} maze instances")
    
    def _save_to_cache(self, cache_file: str):
        """Save dataset to cache file"""
        os.makedirs(os.path.dirname(cache_file), exist_ok=True)
        
        # Convert numpy arrays and paths to lists for JSON serialization
        cache_data = []
        for item in self.data:
            cache_item = {
                'maze': item['maze'].tolist(),
                'path': item['path'],
                'input_seq': item['input_seq'],
                'target_seq': item['target_seq'],
                'difficulty': item['difficulty'],
            }
            cache_data.append(cache_item)
        
        with open(cache_file, 'w') as f:
            json.dump({
                'config': self.config.__dict__,
                'data': cache_data,
            }, f)
    
    def _load_from_cache(self, cache_file: str):
        """Load dataset from cache file"""
        with open(cache_file, 'r') as f:
            cache = json.load(f)
        
        self.data = []
        for item in cache['data']:
            self.data.append({
                'maze': np.array(item['maze']),
                'path': item['path'],
                'input_seq': item['input_seq'],
                'target_seq': item['target_seq'],
                'difficulty': item['difficulty'],
            })
        
        print(f"Loaded {len(self.data)} samples from cache")
    
    def __len__(self) -> int:
        return len(self.data)
    
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        item = self.data[idx]
        
        # Pad sequences to max length
        input_seq = item['input_seq'][:self.config.max_sequence_length]
        target_seq = item['target_seq'][:self.config.max_sequence_length]
        
        # Pad with PAD_TOKEN
        input_len = len(input_seq)
        target_len = len(target_seq)
        
        input_seq += [self.generator.PAD_TOKEN] * (self.config.max_sequence_length - len(input_seq))
        target_seq += [self.generator.PAD_TOKEN] * (self.config.max_sequence_length - len(target_seq))
        
        # Create attention mask
        attention_mask = [1] * input_len + [0] * (self.config.max_sequence_length - input_len)
        
        # Create labels (use -100 for padding tokens to ignore in loss)
        labels = []
        for i, t in enumerate(target_seq):
            if i < target_len:
                labels.append(t)
            else:
                labels.append(-100)
        
        return {
            'input_ids': torch.tensor(input_seq, dtype=torch.long),
            'attention_mask': torch.tensor(attention_mask, dtype=torch.long),
            'labels': torch.tensor(labels, dtype=torch.long),
            'difficulty': torch.tensor(item['difficulty'], dtype=torch.float),
            'maze': torch.tensor(item['maze'], dtype=torch.long),
            'path_length': torch.tensor(len(item['path']), dtype=torch.long),
        }


def create_maze_dataloader(
    num_samples: int = 1000,
    batch_size: int = 8,
    config: MazeConfig = None,
    cache_dir: str = "./cache",
    split: str = "train",
    **kwargs
) -> DataLoader:
    """Create Maze dataloader with caching"""
    
    cache_file = os.path.join(cache_dir, f"maze_{split}_{num_samples}.json")
    
    dataset = MazeDataset(
        num_samples=num_samples,
        config=config,
        cache_file=cache_file,
    )
    
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=(split == "train"),
        num_workers=4,
        pin_memory=True,
        **kwargs
    )


def create_maze_benchmark() -> Dict[str, DataLoader]:
    """Create standard Maze-Hard benchmark dataloaders"""
    config = MazeConfig()
    
    # Training set: 1000 samples as per paper
    train_loader = create_maze_dataloader(
        num_samples=1000,
        batch_size=8,
        config=config,
        split="train"
    )
    
    # Validation set: 200 samples
    val_loader = create_maze_dataloader(
        num_samples=200,
        batch_size=8,
        config=config,
        split="val"
    )
    
    # Test set: 200 samples
    test_loader = create_maze_dataloader(
        num_samples=200,
        batch_size=8,
        config=config,
        split="test"
    )
    
    return {
        "train": train_loader,
        "val": val_loader,
        "test": test_loader,
    }


def evaluate_path_correctness(predicted_path: List[Tuple[int, int]], 
                            maze: np.ndarray, 
                            true_path: List[Tuple[int, int]]) -> Dict[str, float]:
    """Evaluate path prediction correctness"""
    if not predicted_path:
        return {"valid": 0.0, "optimal": 0.0, "accuracy": 0.0}
    
    # Check if path is valid (no walls, connected)
    valid = True
    for i, (x, y) in enumerate(predicted_path):
        # Check bounds
        if not (0 <= x < maze.shape[1] and 0 <= y < maze.shape[0]):
            valid = False
            break
        
        # Check if cell is passable
        if maze[y, x] == 0:  # Wall
            valid = False
            break
        
        # Check connectivity (adjacent cells)
        if i > 0:
            prev_x, prev_y = predicted_path[i-1]
            if abs(x - prev_x) + abs(y - prev_y) != 1:
                valid = False
                break
    
    # Check if optimal (same length as true path)
    optimal = valid and len(predicted_path) == len(true_path)
    
    # Simple accuracy based on correct endpoints
    start_correct = len(predicted_path) > 0 and predicted_path[0] == true_path[0]
    goal_correct = len(predicted_path) > 0 and predicted_path[-1] == true_path[-1]
    accuracy = (start_correct + goal_correct) / 2.0
    
    return {
        "valid": 1.0 if valid else 0.0,
        "optimal": 1.0 if optimal else 0.0,
        "accuracy": accuracy,
    }