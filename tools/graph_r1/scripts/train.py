import torch
from src.agent import Agent
from src.environment import Environment
import pickle
import json

def demonstrate_agent_functionality():
    print("Demonstrating agent functionality (no training)...")

    # Load the knowledge hypergraph
    with open("/Users/admin/AstraTrade-Submission/graph_r1/data/knowledge_hypergraph.pickle", "rb") as f:
        knowledge_hypergraph = pickle.load(f)

    # Load the processed data
    with open("/Users/admin/AstraTrade-Submission/graph_r1/data/cairo_book_processed.json", "r") as f:
        processed_data = json.load(f)

    # Initialize the agent and environment
    agent = Agent()
    env = Environment(knowledge_hypergraph)

    # Demonstrate on a few examples
    for item in processed_data[:2]: # Process first 2 items
        state = env.reset(item['question'])
        print(f"--- New Example ---")
        print(f"Question: {item['question']}")
        done = False
        while not done:
            action_str = agent(str(state))
            # For simplicity, we'll assume the action is always a query
            action = {'type': 'query', 'content': action_str}
            next_state, reward, done = env.step(action)
            print(f"Action: {action['type']}, Content: {action['content']}")
            print(f"Retrieved: {next_state['history'][-1][-1]}")
            state = next_state
            # In this demonstration, we will only do one turn
            done = True

    print("\nDemonstration finished.")
    print("To train the model, you would run the full training loop on a machine with a powerful GPU.")

    # The following is the training loop that would be used for fine-tuning
    # This is commented out to prevent execution on this machine
    """
    optimizer = torch.optim.Adam(agent.parameters(), lr=1e-5)

    for epoch in range(3):
        print(f"Epoch {epoch + 1}")
        for item in processed_data:
            state = env.reset(item['question'])
            done = False
            while not done:
                action_str = agent(str(state))
                action = {'type': 'query', 'content': action_str}
                next_state, reward, done = env.step(action)

                log_probs = torch.tensor([0.5])
                advantages = torch.tensor([reward])

                loss = grpo_loss(log_probs, advantages)
                if loss != 0:
                    optimizer.zero_grad()
                    loss.backward()
                    optimizer.step()

                state = next_state

    print("Finished training.")

    torch.save(agent.state_dict(), "/Users/admin/AstraTrade-Submission/graph_r1/models/graph_r1_agent.pt")
    """

if __name__ == "__main__":
    demonstrate_agent_functionality()
