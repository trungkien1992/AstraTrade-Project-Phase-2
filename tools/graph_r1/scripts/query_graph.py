#!/usr/bin/env python3
"""
Interactive query tool for the enhanced GRAPH-R1 knowledge graph
"""
import pickle
import json
import sys
from typing import Dict, List, Any

def load_knowledge_graph() -> Dict[str, Any]:
    """Load the enhanced knowledge graph"""
    try:
        with open("/Users/admin/AstraTrade-Submission/graph_r1/data/knowledge_hypergraph.pickle", "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        print("Knowledge graph not found. Please run 'init' first.")
        return {}

def query_architecture():
    """Query architectural information"""
    kg = load_knowledge_graph()
    if not kg:
        return
    
    print("\n=== AstraTrade Architecture ===")
    metadata = kg.get("metadata", {})
    print(f"Total Nodes: {metadata.get('total_nodes', 0)}")
    print(f"Total Edges: {metadata.get('total_edges', 0)}")
    print(f"Domains: {', '.join(metadata.get('domains', []))}")
    
    node_types = kg.get("node_types", {})
    
    print("\n=== Domain Breakdown ===")
    for node_type in ["domain", "entity", "service", "cairo_contract", "microservice"]:
        nodes = [node for node, ntype in node_types.items() if ntype == node_type]
        if nodes:
            print(f"{node_type.title()}s: {', '.join(nodes[:10])}")

def query_relationships():
    """Query relationships in the knowledge graph"""
    kg = load_knowledge_graph()
    if not kg:
        return
    
    print("\n=== Key Relationships ===")
    hyperedges = kg.get("hyperedges", [])
    
    # Group by relationship type
    rel_groups = {}
    for rel_type, nodes in hyperedges:
        if rel_type not in rel_groups:
            rel_groups[rel_type] = []
        rel_groups[rel_type].append(nodes)
    
    for rel_type, relationships in rel_groups.items():
        print(f"\n{rel_type.title()}:")
        for rel in relationships[:5]:  # Show first 5
            print(f"  {' -> '.join(rel)}")

def query_domain(domain_name: str):
    """Query specific domain information"""
    kg = load_knowledge_graph()
    if not kg:
        return
    
    print(f"\n=== {domain_name.title()} Domain ===")
    
    # Find domain-related nodes
    node_types = kg.get("node_types", {})
    domain_nodes = []
    
    # Find relationships involving this domain
    hyperedges = kg.get("hyperedges", [])
    domain_relationships = []
    
    for rel_type, nodes in hyperedges:
        if domain_name.lower() in [n.lower() for n in nodes]:
            domain_relationships.append((rel_type, nodes))
    
    if domain_relationships:
        print("Relationships:")
        for rel_type, nodes in domain_relationships:
            print(f"  {rel_type}: {' <-> '.join(nodes)}")
    else:
        print("No specific relationships found.")

def interactive_query():
    """Interactive query interface"""
    print("=== AstraTrade Knowledge Graph Query Tool ===")
    print("Commands:")
    print("  arch - Show architecture overview")
    print("  rel  - Show relationships")
    print("  domain <name> - Query specific domain")
    print("  quit - Exit")
    
    while True:
        try:
            command = input("\nQuery> ").strip().lower()
            
            if command == "quit":
                break
            elif command == "arch":
                query_architecture()
            elif command == "rel":
                query_relationships()
            elif command.startswith("domain "):
                domain_name = command.split(" ", 1)[1]
                query_domain(domain_name)
            else:
                print("Unknown command. Type 'quit' to exit.")
                
        except KeyboardInterrupt:
            break
        except EOFError:
            break
    
    print("\nGoodbye!")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "arch":
            query_architecture()
        elif command == "rel":
            query_relationships()
        elif command.startswith("domain"):
            domain_name = sys.argv[2] if len(sys.argv) > 2 else "trading"
            query_domain(domain_name)
        else:
            print("Usage: python query_graph.py [arch|rel|domain <name>]")
    else:
        interactive_query()