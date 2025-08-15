"""
Test suite for HRM datasets
"""

import torch
import pytest
import numpy as np
import sys
import os
import tempfile
import json

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from datasets.sudoku import SudokuDataset, SudokuGenerator, create_sudoku_dataloader, SudokuConfig
from datasets.maze import MazeDataset, MazeGenerator, create_maze_dataloader, MazeConfig
from datasets.arc import ARCDataset, ARCProcessor, create_arc_dataloader, ARCConfig


class TestSudokuDataset:
    """Test Sudoku dataset implementation"""
    
    def test_sudoku_generator(self):
        """Test Sudoku puzzle generation"""
        config = SudokuConfig()
        generator = SudokuGenerator(config)
        
        # Test puzzle generation
        puzzle, solution, difficulty = generator.generate_puzzle_pair(target_difficulty=10)
        
        assert puzzle.shape == (9, 9)
        assert solution.shape == (9, 9)
        assert isinstance(difficulty, int)
        assert difficulty >= 0
        
        # Check that solution is valid
        for i in range(9):
            # Check rows
            row_values = solution[i]
            assert set(row_values) == set(range(1, 10))
            
            # Check columns
            col_values = solution[:, i]
            assert set(col_values) == set(range(1, 10))
        
        # Check 3x3 boxes
        for box_row in range(3):
            for box_col in range(3):
                box = solution[box_row*3:(box_row+1)*3, box_col*3:(box_col+1)*3]
                box_values = box.flatten()
                assert set(box_values) == set(range(1, 10))
    
    def test_sudoku_validation(self):
        """Test Sudoku validation logic"""
        config = SudokuConfig()
        generator = SudokuGenerator(config)
        
        # Create a test grid
        grid = np.zeros((9, 9), dtype=int)
        
        # Should be valid to place 1 at (0, 0)
        assert generator.is_valid(grid, 0, 0, 1)
        
        # Place 1 at (0, 0)
        grid[0, 0] = 1
        
        # Should not be valid to place 1 again in same row, column, or box
        assert not generator.is_valid(grid, 0, 1, 1)  # Same row
        assert not generator.is_valid(grid, 1, 0, 1)  # Same column
        assert not generator.is_valid(grid, 1, 1, 1)  # Same box
        
        # Should be valid to place 2
        assert generator.is_valid(grid, 0, 1, 2)
    
    def test_sudoku_sequence_conversion(self):
        """Test conversion to sequence format"""
        config = SudokuConfig()
        generator = SudokuGenerator(config)
        
        # Create test grids
        puzzle = np.random.randint(0, 10, (9, 9))
        solution = np.random.randint(1, 10, (9, 9))
        
        input_seq, target_seq = generator.grid_to_sequence(puzzle, solution)
        
        # Check sequence lengths
        assert len(input_seq) == 81 + 1  # Grid + separator
        assert len(target_seq) == 81  # Solution grid
        
        # Check separator token
        assert input_seq[-1] == generator.SEPARATOR_TOKEN
        
        # Check that sequences contain valid tokens
        assert all(0 <= token <= generator.PAD_TOKEN for token in input_seq)
        assert all(1 <= token <= 9 for token in target_seq)
    
    def test_sudoku_dataset(self):
        """Test Sudoku dataset creation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_file = os.path.join(temp_dir, "test_sudoku.json")
            
            dataset = SudokuDataset(
                num_samples=10,
                config=SudokuConfig(),
                difficulty_range=(5, 20),
                augment=False,
                cache_file=cache_file,
            )
            
            assert len(dataset) == 10
            
            # Test dataset item
            item = dataset[0]
            
            assert "input_ids" in item
            assert "attention_mask" in item
            assert "labels" in item
            assert "difficulty" in item
            assert "puzzle" in item
            assert "solution" in item
            
            # Check tensor shapes
            config = SudokuConfig()
            assert item["input_ids"].shape == (config.max_sequence_length,)
            assert item["attention_mask"].shape == (config.max_sequence_length,)
            assert item["labels"].shape == (config.max_sequence_length,)
            assert item["puzzle"].shape == (9, 9)
            assert item["solution"].shape == (9, 9)
    
    def test_sudoku_dataloader(self):
        """Test Sudoku dataloader creation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            dataloader = create_sudoku_dataloader(
                num_samples=20,
                batch_size=4,
                config=SudokuConfig(),
                difficulty_range=(5, 15),
                augment=False,
                cache_dir=temp_dir,
                split="test"
            )
            
            # Test batch
            batch = next(iter(dataloader))
            
            assert batch["input_ids"].shape[0] == 4  # Batch size
            assert batch["labels"].shape[0] == 4
            assert batch["puzzle"].shape == (4, 9, 9)
            assert batch["solution"].shape == (4, 9, 9)


class TestMazeDataset:
    """Test Maze dataset implementation"""
    
    def test_maze_generator(self):
        """Test maze generation"""
        config = MazeConfig()
        generator = MazeGenerator(config)
        
        # Test maze generation
        maze, path, difficulty = generator.create_maze_with_path()
        
        assert maze.shape == (config.maze_size, config.maze_size)
        assert isinstance(path, list)
        assert len(path) >= 2  # At least start and end
        assert isinstance(difficulty, int)
        assert difficulty >= 2
        
        # Check that path is valid
        start, goal = path[0], path[-1]
        assert isinstance(start, tuple) and len(start) == 2
        assert isinstance(goal, tuple) and len(goal) == 2
        
        # Check path connectivity
        for i in range(1, len(path)):
            prev_x, prev_y = path[i-1]
            curr_x, curr_y = path[i]
            
            # Adjacent cells (Manhattan distance = 1)
            distance = abs(curr_x - prev_x) + abs(curr_y - prev_y)
            assert distance == 1, f"Path not connected at step {i}"
    
    def test_maze_pathfinding(self):
        """Test maze pathfinding algorithm"""
        config = MazeConfig()
        generator = MazeGenerator(config)
        
        # Create simple test maze
        maze = np.ones((5, 5), dtype=int)  # All empty
        start = (0, 0)
        goal = (4, 4)
        
        path = generator.find_shortest_path(maze, start, goal)
        
        assert path is not None
        assert path[0] == start
        assert path[-1] == goal
        assert len(path) == 9  # Manhattan distance + 1 for optimal path
    
    def test_maze_sequence_conversion(self):
        """Test conversion to sequence format"""
        config = MazeConfig()
        generator = MazeGenerator(config)
        
        # Create test maze and path
        maze_size = config.maze_size
        maze = np.random.randint(0, 2, (maze_size, maze_size))
        path = [(0, 0), (0, 1), (1, 1), (1, 2)]
        
        input_seq, target_seq = generator.maze_to_sequence(maze, path)
        
        # Check sequence properties
        assert len(input_seq) == maze_size * maze_size
        assert len(target_seq) == len(path) * 2  # x, y coordinates
        
        # Check coordinate encoding
        for i, (x, y) in enumerate(path):
            assert target_seq[i*2] == x
            assert target_seq[i*2 + 1] == y
    
    def test_maze_dataset(self):
        """Test Maze dataset creation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_file = os.path.join(temp_dir, "test_maze.json")
            
            dataset = MazeDataset(
                num_samples=5,
                config=MazeConfig(),
                cache_file=cache_file,
            )
            
            assert len(dataset) == 5
            
            # Test dataset item
            item = dataset[0]
            
            assert "input_ids" in item
            assert "attention_mask" in item
            assert "labels" in item
            assert "difficulty" in item
            assert "maze" in item
            assert "path_length" in item
            
            # Check tensor properties
            config = MazeConfig()
            assert item["input_ids"].shape == (config.max_sequence_length,)
            assert item["maze"].shape == (config.maze_size, config.maze_size)
    
    def test_maze_dataloader(self):
        """Test Maze dataloader creation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            dataloader = create_maze_dataloader(
                num_samples=8,
                batch_size=2,
                config=MazeConfig(),
                cache_dir=temp_dir,
                split="test"
            )
            
            # Test batch
            batch = next(iter(dataloader))
            
            assert batch["input_ids"].shape[0] == 2  # Batch size
            assert batch["labels"].shape[0] == 2
            assert batch["maze"].shape == (2, 30, 30)


class TestARCDataset:
    """Test ARC dataset implementation"""
    
    def test_arc_processor(self):
        """Test ARC data processing"""
        config = ARCConfig()
        processor = ARCProcessor(config)
        
        # Create test task
        test_task = {
            "train": [
                {
                    "input": [[1, 2], [3, 4]],
                    "output": [[2, 1], [4, 3]]
                }
            ],
            "test": [
                {
                    "input": [[5, 6], [7, 8]],
                    "output": [[6, 5], [8, 7]]
                }
            ]
        }
        
        sequences = processor.task_to_sequences(test_task, include_test=True, augment=False)
        
        assert len(sequences) == 2  # 1 train + 1 test
        
        train_seq = sequences[0]
        assert train_seq["type"] == "train"
        assert "input_seq" in train_seq
        assert "output_seq" in train_seq
        assert "input_grid" in train_seq
        assert "output_grid" in train_seq
        
        test_seq = sequences[1]
        assert test_seq["type"] == "test"
    
    def test_arc_grid_padding(self):
        """Test grid padding"""
        config = ARCConfig()
        processor = ARCProcessor(config)
        
        # Test small grid
        small_grid = [[1, 2], [3, 4]]
        padded = processor.pad_grid(small_grid, target_size=5)
        
        assert len(padded) == 5
        assert len(padded[0]) == 5
        assert padded[0][0] == 1
        assert padded[0][1] == 2
        assert padded[1][0] == 3
        assert padded[1][1] == 4
        
        # Padding tokens should be used for empty spaces
        assert padded[0][2] == processor.PAD_TOKEN
        assert padded[2][0] == processor.PAD_TOKEN
    
    def test_arc_transformations(self):
        """Test data augmentation transformations"""
        config = ARCConfig()
        processor = ARCProcessor(config)
        
        # Test grid
        grid = [[1, 2], [3, 4]]
        
        transformations = processor.apply_transformations(grid)
        
        assert len(transformations) >= 3  # At least original + some transforms
        assert transformations[0] == grid  # First should be original
        
        # Check that transformations are different
        assert not all(np.array_equal(t, grid) for t in transformations[1:])
    
    def test_arc_dataset_creation(self):
        """Test ARC dataset creation with mock data"""
        # Create temporary ARC data file
        mock_data = {
            "task1": {
                "train": [
                    {"input": [[1, 2], [3, 4]], "output": [[2, 1], [4, 3]]},
                    {"input": [[5, 6], [7, 8]], "output": [[6, 5], [8, 7]]}
                ],
                "test": [
                    {"input": [[9, 0], [1, 2]], "output": [[0, 9], [2, 1]]}
                ]
            },
            "task2": {
                "train": [
                    {"input": [[0, 1], [1, 0]], "output": [[1, 0], [0, 1]]}
                ],
                "test": [
                    {"input": [[2, 3], [3, 2]], "output": [[3, 2], [2, 3]]}
                ]
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(mock_data, f)
            temp_file = f.name
        
        try:
            # Test dataset creation
            dataset = ARCDataset(
                data_path=temp_file,
                config=ARCConfig(),
                split="train",
                augment=False,
                max_tasks=2,
            )
            
            assert len(dataset) == 3  # 2 tasks × 1-2 examples each
            
            # Test dataset item
            item = dataset[0]
            
            assert "input_ids" in item
            assert "attention_mask" in item
            assert "labels" in item
            assert "task_id" in item
            
            # Check tensor shapes
            config = ARCConfig()
            assert item["input_ids"].shape == (config.max_sequence_length,)
            assert item["attention_mask"].shape == (config.max_sequence_length,)
            assert item["labels"].shape == (config.max_sequence_length,)
            
        finally:
            os.unlink(temp_file)


class TestDatasetIntegration:
    """Test dataset integration and edge cases"""
    
    def test_dataset_caching(self):
        """Test dataset caching functionality"""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_file = os.path.join(temp_dir, "cache_test.json")
            
            # Create dataset with cache
            dataset1 = SudokuDataset(
                num_samples=5,
                config=SudokuConfig(),
                augment=False,
                cache_file=cache_file,
            )
            
            assert os.path.exists(cache_file)
            
            # Load same dataset from cache
            dataset2 = SudokuDataset(
                num_samples=5,
                config=SudokuConfig(),
                augment=False,
                cache_file=cache_file,
            )
            
            # Should have same length
            assert len(dataset1) == len(dataset2)
            
            # Compare first items (should be identical)
            item1 = dataset1[0]
            item2 = dataset2[0]
            
            assert torch.equal(item1["input_ids"], item2["input_ids"])
            assert torch.equal(item1["labels"], item2["labels"])
    
    def test_batch_consistency(self):
        """Test that batches are consistent"""
        with tempfile.TemporaryDirectory() as temp_dir:
            dataloader = create_sudoku_dataloader(
                num_samples=16,
                batch_size=4,
                cache_dir=temp_dir,
                split="test"
            )
            
            batches = list(dataloader)
            assert len(batches) == 4  # 16 samples / 4 batch size
            
            for batch in batches:
                # All tensors in batch should have same shape[0]
                batch_size = batch["input_ids"].shape[0]
                
                for key, tensor in batch.items():
                    if isinstance(tensor, torch.Tensor):
                        assert tensor.shape[0] == batch_size
    
    def test_empty_dataset(self):
        """Test handling of empty datasets"""
        with tempfile.TemporaryDirectory() as temp_dir:
            dataset = SudokuDataset(
                num_samples=0,
                config=SudokuConfig(),
                augment=False,
                cache_file=os.path.join(temp_dir, "empty.json"),
            )
            
            assert len(dataset) == 0
    
    def test_invalid_data_handling(self):
        """Test handling of invalid data"""
        # Test invalid ARC data file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"invalid": "data"}, f)
            invalid_file = f.name
        
        try:
            dataset = ARCDataset(
                data_path=invalid_file,
                config=ARCConfig(),
                split="train",
                max_tasks=1,
            )
            
            # Should handle gracefully (empty dataset or error handling)
            assert len(dataset) >= 0
            
        finally:
            os.unlink(invalid_file)


if __name__ == "__main__":
    pytest.main([__file__])