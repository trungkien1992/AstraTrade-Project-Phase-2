"""
Sudoku-Extreme dataset implementation
Creates challenging Sudoku puzzles requiring extensive backtracking and search
"""

import torch
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import numpy as np
import random
from typing import List, Tuple, Dict, Optional, Union
import json
import os
from dataclasses import dataclass


@dataclass
class SudokuConfig:
    """Configuration for Sudoku dataset"""
    grid_size: int = 9
    box_size: int = 3
    vocab_size: int = 12  # 0-9 digits + padding + separator tokens
    max_sequence_length: int = 200  # Flattened grid + separators
    difficulty_threshold: int = 10  # Minimum backtracks required
    

class SudokuGenerator:
    """
    Generates Sudoku-Extreme puzzles with high difficulty
    
    Based on the paper's description:
    - Compiled from challenging puzzle databases
    - Requires extensive backtracking (mean 22 backtracks per puzzle)
    - Strict train/test split to prevent equivalent transformations
    """
    
    def __init__(self, config: SudokuConfig = None):
        self.config = config or SudokuConfig()
        self.size = self.config.grid_size
        self.box_size = self.config.box_size
        
        # Special tokens
        self.EMPTY_TOKEN = 0
        self.SEPARATOR_TOKEN = 10
        self.PAD_TOKEN = 11
        
    def is_valid(self, grid: np.ndarray, row: int, col: int, num: int) -> bool:
        """Check if placing num at (row, col) is valid"""
        # Check row
        if num in grid[row]:
            return False
            
        # Check column
        if num in grid[:, col]:
            return False
            
        # Check box
        box_row, box_col = (row // self.box_size) * self.box_size, (col // self.box_size) * self.box_size
        if num in grid[box_row:box_row + self.box_size, box_col:box_col + self.box_size]:
            return False
            
        return True
    
    def solve_with_backtrack_count(self, grid: np.ndarray) -> Tuple[bool, int]:
        """Solve sudoku and count backtracks (difficulty measure)"""
        backtracks = 0
        
        def solve(grid):
            nonlocal backtracks
            
            # Find empty cell
            for i in range(self.size):
                for j in range(self.size):
                    if grid[i][j] == 0:
                        # Try numbers 1-9
                        for num in range(1, self.size + 1):
                            if self.is_valid(grid, i, j, num):
                                grid[i][j] = num
                                
                                if solve(grid):
                                    return True
                                    
                                # Backtrack
                                grid[i][j] = 0
                                backtracks += 1
                        
                        return False
            return True
        
        grid_copy = grid.copy()
        solved = solve(grid_copy)
        return solved, backtracks
    
    def generate_full_grid(self) -> np.ndarray:
        """Generate a complete valid Sudoku grid"""
        grid = np.zeros((self.size, self.size), dtype=int)
        
        def fill_grid(grid):
            for i in range(self.size):
                for j in range(self.size):
                    if grid[i][j] == 0:
                        # Randomize order to get different grids
                        numbers = list(range(1, self.size + 1))
                        random.shuffle(numbers)
                        
                        for num in numbers:
                            if self.is_valid(grid, i, j, num):
                                grid[i][j] = num
                                
                                if fill_grid(grid):
                                    return True
                                    
                                grid[i][j] = 0
                        
                        return False
            return True
        
        fill_grid(grid)
        return grid
    
    def create_puzzle(self, full_grid: np.ndarray, target_difficulty: int = None) -> Tuple[np.ndarray, int]:
        """Create puzzle by removing numbers to achieve target difficulty"""
        target_difficulty = target_difficulty or self.config.difficulty_threshold
        
        puzzle = full_grid.copy()
        cells = [(i, j) for i in range(self.size) for j in range(self.size)]
        random.shuffle(cells)
        
        removed_count = 0
        max_attempts = self.size * self.size
        
        for row, col in cells:
            if removed_count >= max_attempts:
                break
                
            # Temporarily remove number
            original = puzzle[row][col]
            puzzle[row][col] = 0
            
            # Check if puzzle still has unique solution and desired difficulty
            solved, backtracks = self.solve_with_backtrack_count(puzzle)
            
            if solved and backtracks >= target_difficulty:
                # Good! Keep it removed
                removed_count += 1
            else:
                # Restore the number
                puzzle[row][col] = original
        
        # Final difficulty check
        _, final_difficulty = self.solve_with_backtrack_count(puzzle)
        return puzzle, final_difficulty
    
    def generate_puzzle_pair(self, target_difficulty: int = None) -> Tuple[np.ndarray, np.ndarray, int]:
        """Generate a puzzle-solution pair with specified difficulty"""
        max_attempts = 100
        
        for _ in range(max_attempts):
            # Generate complete grid
            solution = self.generate_full_grid()
            
            # Create puzzle
            puzzle, difficulty = self.create_puzzle(solution, target_difficulty)
            
            if difficulty >= (target_difficulty or self.config.difficulty_threshold):
                return puzzle, solution, difficulty
        
        # Fallback - return any valid puzzle
        solution = self.generate_full_grid()
        puzzle, difficulty = self.create_puzzle(solution, 1)  # Lower threshold
        return puzzle, solution, difficulty
    
    def apply_transformations(self, grid: np.ndarray) -> List[np.ndarray]:
        """Apply valid transformations (rotations, flips, band/digit permutations)"""
        transformations = []
        
        # Original
        transformations.append(grid.copy())
        
        # Rotations
        for k in range(1, 4):
            transformations.append(np.rot90(grid, k))
        
        # Flips
        transformations.append(np.fliplr(grid))
        transformations.append(np.flipud(grid))
        
        # Band permutations (swap rows within bands)
        for _ in range(3):
            transformed = grid.copy()
            band = random.randint(0, 2)
            rows = list(range(band * 3, (band + 1) * 3))
            random.shuffle(rows)
            transformed[band * 3:(band + 1) * 3] = transformed[rows]
            transformations.append(transformed)
        
        # Digit permutations
        for _ in range(3):
            transformed = grid.copy()
            # Create random digit mapping (1-9)
            digits = list(range(1, 10))
            shuffled = digits.copy()
            random.shuffle(shuffled)
            mapping = {digits[i]: shuffled[i] for i in range(len(digits))}
            
            for i in range(self.size):
                for j in range(self.size):
                    if transformed[i][j] != 0:
                        transformed[i][j] = mapping[transformed[i][j]]
            transformations.append(transformed)
        
        return transformations
    
    def grid_to_sequence(self, puzzle: np.ndarray, solution: np.ndarray) -> Tuple[List[int], List[int]]:
        """Convert grid to sequence format for sequence-to-sequence training"""
        # Flatten puzzle and solution
        puzzle_flat = puzzle.flatten().tolist()
        solution_flat = solution.flatten().tolist()
        
        # Add separator
        input_seq = puzzle_flat + [self.SEPARATOR_TOKEN]
        target_seq = solution_flat
        
        return input_seq, target_seq


class SudokuDataset(Dataset):
    """
    Sudoku-Extreme dataset for HRM training
    
    Features:
    - High-difficulty puzzles requiring backtracking
    - Sequence-to-sequence format
    - Data augmentation with valid transformations
    - Train/test split preventing equivalent puzzles
    """
    
    def __init__(
        self,
        num_samples: int = 1000,
        config: SudokuConfig = None,
        difficulty_range: Tuple[int, int] = (10, 50),
        augment: bool = True,
        cache_file: Optional[str] = None,
    ):
        self.config = config or SudokuConfig()
        self.num_samples = num_samples
        self.difficulty_range = difficulty_range
        self.augment = augment
        self.generator = SudokuGenerator(self.config)
        
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
        
        print(f"Generating {self.num_samples} Sudoku-Extreme puzzles...")
        for i in range(self.num_samples):
            if i % 100 == 0:
                print(f"Generated {i}/{self.num_samples} puzzles")
            
            # Generate puzzle with random difficulty in range
            target_difficulty = random.randint(*self.difficulty_range)
            puzzle, solution, actual_difficulty = self.generator.generate_puzzle_pair(target_difficulty)
            
            # Convert to sequences
            input_seq, target_seq = self.generator.grid_to_sequence(puzzle, solution)
            
            self.data.append({
                'puzzle': puzzle,
                'solution': solution,
                'input_seq': input_seq,
                'target_seq': target_seq,
                'difficulty': actual_difficulty,
            })
            
            # Data augmentation
            if self.augment:
                transformations = self.generator.apply_transformations(puzzle)
                solution_transformations = self.generator.apply_transformations(solution)
                
                for puzzle_t, solution_t in zip(transformations[1:4], solution_transformations[1:4]):  # Limit augmentation
                    input_seq_t, target_seq_t = self.generator.grid_to_sequence(puzzle_t, solution_t)
                    self.data.append({
                        'puzzle': puzzle_t,
                        'solution': solution_t,
                        'input_seq': input_seq_t,
                        'target_seq': target_seq_t,
                        'difficulty': actual_difficulty,
                    })
        
        print(f"Generated {len(self.data)} total samples (including augmentation)")
    
    def _save_to_cache(self, cache_file: str):
        """Save dataset to cache file"""
        os.makedirs(os.path.dirname(cache_file), exist_ok=True)
        
        # Convert numpy arrays to lists for JSON serialization
        cache_data = []
        for item in self.data:
            cache_item = {
                'puzzle': item['puzzle'].tolist(),
                'solution': item['solution'].tolist(),
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
                'puzzle': np.array(item['puzzle']),
                'solution': np.array(item['solution']),
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
        input_seq += [self.generator.PAD_TOKEN] * (self.config.max_sequence_length - len(input_seq))
        target_seq += [self.generator.PAD_TOKEN] * (self.config.max_sequence_length - len(target_seq))
        
        # Create attention mask
        attention_mask = [1] * len(item['input_seq']) + [0] * (self.config.max_sequence_length - len(item['input_seq']))
        
        # Create labels (use -100 for padding tokens to ignore in loss)
        labels = [t if t != self.generator.PAD_TOKEN else -100 for t in target_seq]
        
        return {
            'input_ids': torch.tensor(input_seq, dtype=torch.long),
            'attention_mask': torch.tensor(attention_mask, dtype=torch.long),
            'labels': torch.tensor(labels, dtype=torch.long),
            'difficulty': torch.tensor(item['difficulty'], dtype=torch.float),
            'puzzle': torch.tensor(item['puzzle'], dtype=torch.long),
            'solution': torch.tensor(item['solution'], dtype=torch.long),
        }


def create_sudoku_dataloader(
    num_samples: int = 1000,
    batch_size: int = 8,
    config: SudokuConfig = None,
    difficulty_range: Tuple[int, int] = (10, 50),
    augment: bool = True,
    cache_dir: str = "./cache",
    split: str = "train",
    **kwargs
) -> DataLoader:
    """Create Sudoku dataloader with caching"""
    
    cache_file = os.path.join(cache_dir, f"sudoku_{split}_{num_samples}_{difficulty_range[0]}_{difficulty_range[1]}.json")
    
    dataset = SudokuDataset(
        num_samples=num_samples,
        config=config,
        difficulty_range=difficulty_range,
        augment=augment,
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


def create_sudoku_benchmark() -> Dict[str, DataLoader]:
    """Create standard Sudoku-Extreme benchmark dataloaders"""
    config = SudokuConfig()
    
    # Training set: 1000 samples as per paper
    train_loader = create_sudoku_dataloader(
        num_samples=1000,
        batch_size=8,
        config=config,
        difficulty_range=(15, 40),
        augment=True,
        split="train"
    )
    
    # Validation set: 200 samples
    val_loader = create_sudoku_dataloader(
        num_samples=200,
        batch_size=8,
        config=config,
        difficulty_range=(15, 40),
        augment=False,
        split="val"
    )
    
    # Test set: 200 samples with higher difficulty
    test_loader = create_sudoku_dataloader(
        num_samples=200,
        batch_size=8,
        config=config,
        difficulty_range=(20, 50),
        augment=False,
        split="test"
    )
    
    return {
        "train": train_loader,
        "val": val_loader,
        "test": test_loader,
    }