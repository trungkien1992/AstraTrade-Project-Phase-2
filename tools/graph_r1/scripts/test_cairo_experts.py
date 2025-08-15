#!/usr/bin/env python3
"""
Test script for Cairo Expert Sub-Agent system
"""
import sys
import pickle
sys.path.append('/Users/admin/AstraTrade-Submission/graph_r1')

from src.cairo_expert_system import CairoExpertCoordinator

def test_cairo_experts():
    """Test the Cairo expert system with various queries"""
    
    # Load knowledge graph
    try:
        with open("/Users/admin/AstraTrade-Submission/graph_r1/data/knowledge_hypergraph.pickle", "rb") as f:
            knowledge_graph = pickle.load(f)
    except FileNotFoundError:
        print("Knowledge graph not found. Please run 'graph_r1_cli.py init' first.")
        return
    
    coordinator = CairoExpertCoordinator(knowledge_graph)
    
    # Test queries
    test_queries = [
        {
            "query": "How do I implement a constructor in Cairo?",
            "expected_agent": "development"
        },
        {
            "query": "What are the security best practices for access control?",
            "expected_agent": "security"
        },
        {
            "query": "How to prevent reentrancy attacks in Cairo?",
            "expected_agent": "security"
        },
        {
            "query": "What are the different function types in Cairo contracts?",
            "expected_agent": "development"
        }
    ]
    
    print("=== Cairo Expert System Test ===\n")
    
    for i, test in enumerate(test_queries, 1):
        query = test["query"]
        expected = test["expected_agent"]
        
        print(f"Test {i}: {query}")
        print("-" * 60)
        
        # Auto-route the query
        result = coordinator.route_query(query)
        
        routing_info = result.get("routing_info", {})
        selected_agent = routing_info.get("selected_agent", "unknown")
        confidence = routing_info.get("confidence", 0)
        
        print(f"Selected Agent: {selected_agent}")
        print(f"Confidence: {confidence:.2f}")
        print(f"Expected: cairo_{expected}")
        
        # Check if routing was correct
        if expected in selected_agent:
            print("✅ Routing: CORRECT")
        else:
            print("❌ Routing: INCORRECT")
        
        # Show key guidance
        if 'guidance' in result:
            print("\nKey Guidance Areas:")
            for key in list(result['guidance'].keys())[:3]:
                print(f"  • {key.replace('_', ' ').title()}")
        
        print("\n" + "="*60 + "\n")

    # Test collaborative analysis
    print("=== Collaborative Analysis Test ===\n")
    
    collaborative_query = "How to implement and audit access control in Cairo smart contracts?"
    print(f"Query: {collaborative_query}")
    print("-" * 60)
    
    collab_result = coordinator.collaborative_analysis(collaborative_query)
    
    print("Participating Agents:")
    for agent_type in collab_result["agent_responses"].keys():
        print(f"  • {agent_type.replace('_', ' ').title()}")
    
    synthesis = collab_result.get("synthesis", {})
    if synthesis.get("key_insights"):
        print("\nKey Insights:")
        for insight in synthesis["key_insights"]:
            print(f"  • {insight}")
    
    print("\n" + "="*60 + "\n")

def demonstrate_expert_capabilities():
    """Demonstrate detailed expert capabilities"""
    
    try:
        with open("/Users/admin/AstraTrade-Submission/graph_r1/data/knowledge_hypergraph.pickle", "rb") as f:
            knowledge_graph = pickle.load(f)
    except FileNotFoundError:
        print("Knowledge graph not found. Please run 'graph_r1_cli.py init' first.")
        return
    
    coordinator = CairoExpertCoordinator(knowledge_graph)
    
    print("=== Cairo Development Expert Demo ===\n")
    
    dev_query = "How do I implement storage in Cairo contracts?"
    dev_result = coordinator.get_specialized_guidance("development", dev_query)
    
    print(f"Query: {dev_query}")
    print(f"Agent: {dev_result.get('agent', 'Unknown')}")
    print(f"Query Type: {dev_result.get('query_type', 'Unknown')}")
    
    if 'guidance' in dev_result:
        guidance = dev_result['guidance']
        print("\nStorage Types:")
        if 'storage_types' in guidance:
            for storage_type, details in guidance['storage_types'].items():
                print(f"  • {storage_type.replace('_', ' ').title()}: {details.get('syntax', 'N/A')}")
    
    if 'code_examples' in dev_result:
        print(f"\nCode Examples Available: {len(dev_result['code_examples'])}")
    
    print("\n" + "="*60 + "\n")
    
    print("=== Cairo Security Expert Demo ===\n")
    
    sec_query = "What access control vulnerabilities should I check for?"
    sec_result = coordinator.get_specialized_guidance("security", sec_query)
    
    print(f"Query: {sec_query}")
    print(f"Agent: {sec_result.get('agent', 'Unknown')}")
    print(f"Query Type: {sec_result.get('query_type', 'Unknown')}")
    
    if 'security_analysis' in sec_result:
        analysis = sec_result['security_analysis']
        print("\nSecurity Patterns:")
        if 'owner_pattern' in analysis:
            vulnerabilities = analysis['owner_pattern'].get('vulnerabilities', [])
            print(f"  • Owner Pattern Vulnerabilities: {len(vulnerabilities)}")
            for vuln in vulnerabilities[:2]:
                print(f"    - {vuln}")
    
    if 'audit_checklist' in sec_result:
        print(f"\nAudit Checklist Items: {len(sec_result['audit_checklist'])}")
        for item in sec_result['audit_checklist'][:3]:
            print(f"  • {item}")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    print("Cairo Expert Sub-Agent System Test\n")
    
    print("1. Testing Agent Routing...")
    test_cairo_experts()
    
    print("2. Demonstrating Expert Capabilities...")
    demonstrate_expert_capabilities()
    
    print("✅ Cairo Expert System Tests Complete!")