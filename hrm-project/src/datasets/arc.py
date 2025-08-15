"""
ARC-AGI dataset implementation
Handles ARC (Abstraction and Reasoning Corpus) challenge data
"""

import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np
import json
import os
from typing import List, Tuple, Dict, Optional, Union, Any
from dataclasses import dataclass
import random


@dataclass
class ARCConfig:
    """Configuration for ARC dataset"""
    max_grid_size: int = 30
    vocab_size: int = 12  # 10 colors + padding + separator
    max_sequence_length: int = 2000
    max_examples: int = 10  # Maximum training examples per task
    

class ARCProcessor:
    """
    Processes ARC tasks for sequence-to-sequence training
    
    Based on the paper's approach:
    - Grid-based inductive reasoning tasks
    - Few-shot learning (2-3 examples per task)
    - Data augmentation with transformations
    - 30x30 grid context (900 tokens)
    """
    
    def __init__(self, config: ARCConfig = None):
        self.config = config or ARCConfig()
        
        # Special tokens
        self.PAD_TOKEN = 10
        self.SEP_TOKEN = 11  # Separator between input and output grids
        
    def grid_to_sequence(self, grid: List[List[int]]) -> List[int]:
        """Convert 2D grid to flattened sequence"""
        sequence = []
        for row in grid:
            sequence.extend(row)
        return sequence
    
    def pad_grid(self, grid: List[List[int]], target_size: int = None) -> List[List[int]]:
        """Pad grid to target size"""
        target_size = target_size or self.config.max_grid_size
        
        # Current dimensions
        height = len(grid)
        width = len(grid[0]) if height > 0 else 0
        
        # Pad rows
        padded_grid = []
        for row in grid:
            padded_row = row + [self.PAD_TOKEN] * (target_size - len(row))
            padded_grid.append(padded_row[:target_size])  # Truncate if too large
        
        # Pad columns
        while len(padded_grid) < target_size:
            padded_grid.append([self.PAD_TOKEN] * target_size)
        
        return padded_grid[:target_size]  # Truncate if too large
    
    def apply_transformations(self, grid: List[List[int]]) -> List[List[List[int]]]:
        """Apply transformations for data augmentation"""
        grid_array = np.array(grid)
        transformations = []
        
        # Original
        transformations.append(grid)
        
        # Rotations
        for k in range(1, 4):
            rotated = np.rot90(grid_array, k).tolist()
            transformations.append(rotated)
        
        # Flips
        flipped_lr = np.fliplr(grid_array).tolist()
        flipped_ud = np.flipud(grid_array).tolist()
        transformations.append(flipped_lr)
        transformations.append(flipped_ud)
        
        # Color permutations
        unique_colors = list(set([cell for row in grid for cell in row if cell != self.PAD_TOKEN]))
        if len(unique_colors) > 1:
            # Create a random color permutation
            shuffled_colors = unique_colors.copy()
            random.shuffle(shuffled_colors)
            color_map = {unique_colors[i]: shuffled_colors[i] for i in range(len(unique_colors))}
            
            permuted_grid = []
            for row in grid:
                permuted_row = [color_map.get(cell, cell) for cell in row]
                permuted_grid.append(permuted_row)
            transformations.append(permuted_grid)
        
        return transformations
    
    def task_to_sequences(
        self,
        task: Dict[str, Any],
        include_test: bool = False,
        augment: bool = False,
    ) -> List[Dict[str, Any]]:
        """Convert ARC task to sequence-to-sequence format"""
        sequences = []
        
        # Process training examples
        train_examples = task.get("train", [])
        for example in train_examples:
            input_grid = example["input"]
            output_grid = example["output"]
            
            # Pad grids
            input_padded = self.pad_grid(input_grid)
            output_padded = self.pad_grid(output_grid)
            
            # Convert to sequences
            input_seq = self.grid_to_sequence(input_padded)
            output_seq = self.grid_to_sequence(output_padded)
            
            sequences.append({
                "input_seq": input_seq,
                "output_seq": output_seq,
                "input_grid": input_padded,
                "output_grid": output_padded,
                "task_id": task.get("id", "unknown"),
                "type": "train"
            })
            
            # Data augmentation
            if augment:
                input_transforms = self.apply_transformations(input_grid)
                output_transforms = self.apply_transformations(output_grid)
                
                for inp_t, out_t in zip(input_transforms[1:4], output_transforms[1:4]):  # Limit to 3 transforms
                    inp_padded = self.pad_grid(inp_t)
                    out_padded = self.pad_grid(out_t)
                    
                    sequences.append({
                        "input_seq": self.grid_to_sequence(inp_padded),
                        "output_seq": self.grid_to_sequence(out_padded),
                        "input_grid": inp_padded,
                        "output_grid": out_padded,
                        "task_id": task.get("id", "unknown"),
                        "type": "train_augmented"
                    })
        
        # Process test examples if requested
        if include_test:
            test_examples = task.get("test", [])
            for example in test_examples:
                input_grid = example["input"]
                output_grid = example.get("output", None)  # May not be available
                
                input_padded = self.pad_grid(input_grid)
                input_seq = self.grid_to_sequence(input_padded)
                
                if output_grid is not None:
                    output_padded = self.pad_grid(output_grid)
                    output_seq = self.grid_to_sequence(output_padded)
                else:
                    output_padded = None
                    output_seq = None
                
                sequences.append({
                    "input_seq": input_seq,
                    "output_seq": output_seq,
                    "input_grid": input_padded,
                    "output_grid": output_padded,
                    "task_id": task.get("id", "unknown"),
                    "type": "test"
                })
        
        return sequences
    
    def create_few_shot_sequence(
        self,
        task: Dict[str, Any],
        test_input: List[List[int]],
    ) -> Tuple[List[int], List[List[int]]]:
        """Create few-shot sequence with examples + test input"""
        sequence = []
        
        # Add training examples
        train_examples = task.get("train", [])[:self.config.max_examples]
        
        for example in train_examples:
            input_grid = self.pad_grid(example["input"])
            output_grid = self.pad_grid(example["output"])
            
            # Add input grid
            sequence.extend(self.grid_to_sequence(input_grid))
            sequence.append(self.SEP_TOKEN)
            
            # Add output grid
            sequence.extend(self.grid_to_sequence(output_grid))
            sequence.append(self.SEP_TOKEN)
        
        # Add test input
        test_input_padded = self.pad_grid(test_input)
        sequence.extend(self.grid_to_sequence(test_input_padded))
        sequence.append(self.SEP_TOKEN)
        
        return sequence, test_input_padded


class ARCDataset(Dataset):
    """
    ARC-AGI dataset for HRM training
    
    Features:
    - Inductive reasoning tasks
    - Few-shot learning format
    - Grid-based puzzles
    - Data augmentation with transformations
    """
    
    def __init__(
        self,
        data_path: str,
        config: ARCConfig = None,
        split: str = "train",
        augment: bool = True,
        max_tasks: Optional[int] = None,
    ):
        self.config = config or ARCConfig()
        self.split = split
        self.augment = augment
        self.processor = ARCProcessor(self.config)
        
        # Load ARC data
        self.data = self._load_arc_data(data_path, max_tasks)
        
        print(f"Loaded {len(self.data)} {split} sequences from ARC dataset")
    
    def _load_arc_data(self, data_path: str, max_tasks: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load ARC data from JSON files"""
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"ARC data not found at {data_path}")
        
        # Load JSON data
        with open(data_path, 'r') as f:
            tasks = json.load(f)
        
        # Convert tasks to sequences
        all_sequences = []
        task_count = 0
        
        for task_id, task_data in tasks.items():
            if max_tasks and task_count >= max_tasks:
                break
            
            task_data["id"] = task_id
            sequences = self.processor.task_to_sequences(
                task_data,
                include_test=(self.split == "test"),
                augment=self.augment and (self.split == "train")
            )
            
            all_sequences.extend(sequences)
            task_count += 1
        
        return all_sequences
    
    def __len__(self) -> int:
        return len(self.data)
    
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        item = self.data[idx]
        
        # Get sequences
        input_seq = item["input_seq"][:self.config.max_sequence_length]
        output_seq = item["output_seq"][:self.config.max_sequence_length] if item["output_seq"] else []
        
        # Pad sequences
        input_len = len(input_seq)
        output_len = len(output_seq)
        
        input_seq += [self.processor.PAD_TOKEN] * (self.config.max_sequence_length - len(input_seq))
        output_seq += [self.processor.PAD_TOKEN] * (self.config.max_sequence_length - len(output_seq))
        
        # Create attention mask
        attention_mask = [1] * input_len + [0] * (self.config.max_sequence_length - input_len)
        
        # Create labels
        labels = []
        for i, token in enumerate(output_seq):
            if i < output_len:
                labels.append(token)
            else:
                labels.append(-100)  # Ignore padding in loss
        
        result = {
            'input_ids': torch.tensor(input_seq, dtype=torch.long),
            'attention_mask': torch.tensor(attention_mask, dtype=torch.long),
            'labels': torch.tensor(labels, dtype=torch.long),
            'task_id': item["task_id"],
        }
        
        # Add grids if available
        if item["input_grid"]:
            result['input_grid'] = torch.tensor(item["input_grid"], dtype=torch.long)
        if item["output_grid"]:
            result['output_grid'] = torch.tensor(item["output_grid"], dtype=torch.long)
        
        return result


def create_arc_dataloader(
    data_path: str,
    batch_size: int = 4,
    config: ARCConfig = None,
    split: str = "train",
    augment: bool = True,
    max_tasks: Optional[int] = None,
    **kwargs
) -> DataLoader:
    """Create ARC dataloader"""
    
    dataset = ARCDataset(
        data_path=data_path,
        config=config,
        split=split,
        augment=augment,
        max_tasks=max_tasks,
    )
    
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=(split == "train"),
        num_workers=2,  # Lower for ARC due to complexity
        pin_memory=True,
        **kwargs
    )


def create_arc_benchmark(data_dir: str) -> Dict[str, DataLoader]:
    """Create standard ARC-AGI benchmark dataloaders"""
    config = ARCConfig()
    
    # Paths for ARC data files
    train_path = os.path.join(data_dir, "arc-agi_training_challenges.json")
    eval_path = os.path.join(data_dir, "arc-agi_evaluation_challenges.json")
    test_path = os.path.join(data_dir, "arc-agi_test_challenges.json")
    
    loaders = {}
    
    # Training set
    if os.path.exists(train_path):
        loaders["train"] = create_arc_dataloader(
            data_path=train_path,
            batch_size=4,
            config=config,
            split="train",
            augment=True,
            max_tasks=960,  # As per paper
        )
    
    # Evaluation set (ARC-AGI-1)
    if os.path.exists(eval_path):
        loaders["eval"] = create_arc_dataloader(
            data_path=eval_path,
            batch_size=4,
            config=config,
            split="test",
            augment=False,
        )
    
    # Test set (ARC-AGI-2)
    if os.path.exists(test_path):
        loaders["test"] = create_arc_dataloader(
            data_path=test_path,
            batch_size=4,
            config=config,
            split="test",
            augment=False,
            max_tasks=1120,  # As per paper
        )
    
    return loaders


def evaluate_arc_prediction(
    predicted_grid: torch.Tensor,
    target_grid: torch.Tensor,
    pad_token: int = 10,
) -> Dict[str, float]:
    """Evaluate ARC grid prediction"""
    # Remove padding
    pred_np = predicted_grid.cpu().numpy()
    target_np = target_grid.cpu().numpy()
    
    # Find valid region (non-padded)
    valid_mask = target_np != pad_token
    
    if not valid_mask.any():
        return {"exact_match": 0.0, "pixel_accuracy": 0.0}
    
    # Extract valid regions
    pred_valid = pred_np[valid_mask]
    target_valid = target_np[valid_mask]
    
    # Exact match (all pixels correct)
    exact_match = float(np.array_equal(pred_valid, target_valid))
    
    # Pixel accuracy
    pixel_accuracy = float(np.mean(pred_valid == target_valid))
    
    return {
        "exact_match": exact_match,
        "pixel_accuracy": pixel_accuracy,
    }


def download_arc_data(data_dir: str):
    """Download ARC-AGI dataset"""
    import urllib.request
    import tarfile
    
    os.makedirs(data_dir, exist_ok=True)
    
    # URLs for ARC dataset
    urls = {
        "training": "https://github.com/fchollet/ARC/raw/master/data/training.json",
        "evaluation": "https://github.com/fchollet/ARC/raw/master/data/evaluation.json",
        "test": "https://github.com/fchollet/ARC/raw/master/data/test.json",
    }
    
    for name, url in urls.items():
        filename = f"arc-agi_{name}_challenges.json"
        filepath = os.path.join(data_dir, filename)
        
        if not os.path.exists(filepath):
            print(f"Downloading {name} data...")
            urllib.request.urlretrieve(url, filepath)
            print(f"Downloaded to {filepath}")
        else:
            print(f"{name} data already exists at {filepath}")
    
    print("ARC dataset download complete!")