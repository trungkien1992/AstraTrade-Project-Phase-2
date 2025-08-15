from src.agent import Agent
import json

def evaluate():
    print("Evaluating the agent...")

    # Load the pre-trained agent
    agent = Agent()

    # Load the test data
    with open("/Users/admin/AstraTrade-Submission/graph_r1/data/cairo_book_processed.json", "r") as f:
        test_data = json.load(f)

    # Qualitative evaluation
    for item in test_data[:2]: # Evaluate on first 2 items
        print(f"--- New Example ---")
        print(f"Supporting Fact: {item['supporting_facts'][0]}")
        # In a real scenario, we would have a question here
        # For now, we will use the supporting fact as the input to the agent
        answer = agent(item['supporting_facts'][0])
        print(f"Generated Answer: {answer}")

if __name__ == "__main__":
    evaluate()
