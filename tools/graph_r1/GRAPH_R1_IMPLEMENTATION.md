
# GRAPH-R1 Implementation Plan

This document outlines the steps to implement the GRAPH-R1 paper.

## 1. Project Setup

- **Objective:** Create the project structure and set up the environment.
- **Actions:**
    1. Create the following directories: `graph_r1/src`, `graph_r1/scripts`, `graph_r1/data`, `graph_r1/models`.
    2. Create a Python virtual environment.
    3. Install the necessary libraries: `transformers`, `torch`, `datasets`, `faiss-cpu`, `sentence-transformers`, `tqdm`.
    4. Create a `requirements.txt` file.

## 2. Data Preparation

- **Objective:** Download and preprocess the HotpotQA dataset.
- **Script:** `scripts/prepare_data.py`
- **Actions:**
    1. Load the HotpotQA dataset from the `datasets` library.
    2. For each sample, extract the question, answer, and supporting facts.
    3. Save the processed data in a JSON format to `data/hotpotqa_processed.json`.

## 3. Knowledge Hypergraph Construction

- **Objective:** Build the knowledge hypergraph from the preprocessed data.
- **Module:** `src/knowledge_graph.py`
- **Script:** `scripts/build_knowledge_graph.py`
- **Actions:**
    1. **N-ary Relation Extraction:**
        - Use a pre-trained model (e.g., from the `transformers` library) to extract entities and relations from the supporting facts.
    2. **Hypergraph Creation:**
        - Represent the extracted information as a hypergraph, where entities are nodes and relations are hyperedges.
    3. **Embeddings:**
        - Use a sentence transformer model to generate embeddings for all nodes and hyperedges.
    4. **Save:**
        - Save the constructed hypergraph object (including embeddings) to `data/knowledge_hypergraph.pickle`.

## 4. Agent and Environment

- **Objective:** Define the Graph-R1 agent and the interaction environment.
- **Module:** `src/agent.py`
    - Define the agent class, which will include the policy model (a transformer-based language model).
    - Implement the action selection logic (think, query, answer).
- **Module:** `src/environment.py`
    - Define the environment class, which will manage the state.
    - Implement the hypergraph retrieval mechanism.
    - Implement the reward function as defined in the paper.

## 5. Reinforcement Learning (GRPO)

- **Objective:** Implement the GRPO algorithm and the training loop.
- **Module:** `src/grpo.py`
    - Implement the GRPO loss function.
- **Script:** `scripts/train.py`
    - **Initialization:** Load the agent, environment, and hypergraph.
    - **Training Loop:**
        - For each epoch and each data sample:
            - The agent interacts with the environment to generate a trajectory.
            - Calculate the reward for the trajectory.
            - Use the GRPO algorithm to update the agent's policy.
    - **Save Model:** Save the trained agent's model weights to `models/graph_r1_agent.pt`.

## 6. Evaluation

- **Objective:** Evaluate the performance of the trained agent.
- **Script:** `scripts/evaluate.py`
- **Actions:**
    1. Load the trained agent and the test set.
    2. For each sample in the test set, let the agent generate an answer.
    3. Compute and report the following metrics:
        - F1 Score
        - Exact Match (EM)
        - Retrieval Similarity (R-S)

## 7. Main Execution Script

- **Objective:** Create a single script to run the entire pipeline.
- **Script:** `run.sh`
- **Content:**
    ```bash
    #!/bin/bash
    echo "Step 1: Preparing data..."
    python scripts/prepare_data.py

    echo "Step 2: Building knowledge hypergraph..."
    python scripts/build_knowledge_graph.py

    echo "Step 3: Training the agent..."
    python scripts/train.py

    echo "Step 4: Evaluating the agent..."
    python scripts/evaluate.py
    ```
