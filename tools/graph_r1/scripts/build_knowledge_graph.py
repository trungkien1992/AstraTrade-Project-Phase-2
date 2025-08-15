import pickle
import json
from typing import Dict, List, Any, Set, Tuple
from pathlib import Path

def build_knowledge_graph():
    print("Building AstraTrade knowledge hypergraph...")
    
    # Load processed data
    data_file = "/Users/admin/AstraTrade-Submission/graph_r1/data/cairo_book_processed.json"
    with open(data_file, "r") as f:
        processed_data = json.load(f)
    
    # Build comprehensive knowledge graph
    knowledge_hypergraph = build_enhanced_graph(processed_data)
    
    with open("/Users/admin/AstraTrade-Submission/graph_r1/data/knowledge_hypergraph.pickle", "wb") as f:
        pickle.dump(knowledge_hypergraph, f)
    
    print(f"Built knowledge hypergraph with {len(knowledge_hypergraph['nodes'])} nodes and {len(knowledge_hypergraph['hyperedges'])} hyperedges")
    print("Saved enhanced knowledge hypergraph to data/knowledge_hypergraph.pickle")

def build_enhanced_graph(processed_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Build enhanced knowledge graph from processed AstraTrade data"""
    
    nodes = set()
    hyperedges = []
    node_types = {}
    relationships = []
    
    # Extract entities and relationships from processed data
    for item in processed_data:
        supporting_facts = item.get("supporting_facts", [])
        answer = item.get("answer", "")
        
        for fact in supporting_facts:
            entities, relations = extract_entities_and_relations(fact, answer)
            nodes.update(entities.keys())
            node_types.update(entities)
            relationships.extend(relations)
    
    # Add core AstraTrade concepts
    core_concepts = add_core_astratrade_concepts()
    nodes.update(core_concepts.keys())
    node_types.update(core_concepts)
    
    # Build hyperedges from relationships
    hyperedges = build_hyperedges_from_relationships(relationships)
    
    # Generate embeddings (simplified)
    embeddings = generate_simplified_embeddings(nodes, hyperedges)
    
    return {
        "nodes": list(nodes),
        "node_types": node_types,
        "hyperedges": hyperedges,
        "embeddings": embeddings,
        "metadata": {
            "total_nodes": len(nodes),
            "total_edges": len(hyperedges),
            "domains": get_domain_list(node_types)
        }
    }

def extract_entities_and_relations(fact: str, context: str) -> Tuple[Dict[str, str], List[Tuple[str, str, str]]]:
    """Extract entities and relationships from text"""
    entities = {}
    relations = []
    
    # Domain detection
    if "Domain:" in fact:
        domain_match = fact.split("Domain: ")[1].split(" |")[0] if " |" in fact else fact.split("Domain: ")[1]
        entities[domain_match] = "domain"
        
        # Extract classes from domain info
        if "entities.py:" in fact:
            classes_part = fact.split("entities.py: ")[1].split(" |")[0] if " |" in fact else fact.split("entities.py: ")[1]
            for class_name in classes_part.split(", "):
                if class_name.strip():
                    entities[class_name.strip()] = "entity"
                    relations.append(("belongs_to", class_name.strip(), domain_match))
        
        if "services.py:" in fact:
            services_part = fact.split("services.py: ")[1].split(" |")[0] if " |" in fact else fact.split("services.py: ")[1]
            for service_name in services_part.split(", "):
                if service_name.strip():
                    entities[service_name.strip()] = "service"
                    relations.append(("serves", service_name.strip(), domain_match))
    
    # Contract detection
    if "Contract:" in fact:
        contract_match = fact.split("Contract: ")[1].split(" |")[0] if " |" in fact else fact.split("Contract: ")[1]
        entities[contract_match.replace(".cairo", "")] = "cairo_contract"
        
        if "Functions:" in fact:
            functions_part = fact.split("Functions: ")[1].split(" |")[0] if " |" in fact else fact.split("Functions: ")[1]
            for func_name in functions_part.split(", "):
                if func_name.strip():
                    entities[func_name.strip()] = "function"
                    relations.append(("implements", func_name.strip(), contract_match.replace(".cairo", "")))
    
    # Service detection
    if "Service:" in fact:
        service_match = fact.split("Service: ")[1].split(" |")[0] if " |" in fact else fact.split("Service: ")[1]
        entities[service_match] = "microservice"
    
    return entities, relations

def add_core_astratrade_concepts() -> Dict[str, str]:
    """Add core AstraTrade architectural concepts"""
    return {
        "AstraTrade": "platform",
        "Cairo": "programming_language",
        "Starknet": "blockchain",
        "Trading": "domain",
        "Gamification": "domain", 
        "Financial": "domain",
        "Social": "domain",
        "NFT": "domain",
        "User": "domain",
        "Event_Sourcing": "pattern",
        "Redis_Streams": "technology",
        "Microservices": "architecture",
        "Domain_Driven_Design": "pattern",
        "CQRS": "pattern",
        # Cairo-specific concepts
        "felt252": "cairo_data_type",
        "ContractAddress": "starknet_type",
        "ContractState": "cairo_state_management",
        "StoragePointer": "cairo_storage",
        "Map": "cairo_collection",
        "access_control": "cairo_security_pattern",
        "assert": "cairo_validation",
        "constructor": "cairo_function_type",
        "external": "cairo_function_type",
        "view": "cairo_function_type",
        "internal": "cairo_function_type",
        "abi_embed_v0": "cairo_attribute",
        "external_v0": "cairo_attribute",
        "starknet_interface": "cairo_attribute",
        "starknet_contract": "cairo_attribute",
        "storage": "cairo_attribute",
        "CEI_pattern": "cairo_security_pattern",
        "ownership_system": "cairo_memory_model",
        "Sierra": "cairo_ir",
        "CASM": "cairo_assembly",
        "Cairo_VM": "execution_environment"
    }

def build_hyperedges_from_relationships(relationships: List[Tuple[str, str, str]]) -> List[Tuple[str, List[str]]]:
    """Build hyperedges from extracted relationships"""
    hyperedges = []
    
    # Group relationships by type
    relation_groups = {}
    for rel_type, source, target in relationships:
        if rel_type not in relation_groups:
            relation_groups[rel_type] = []
        relation_groups[rel_type].append([source, target])
    
    # Convert to hyperedges
    for rel_type, pairs in relation_groups.items():
        for pair in pairs:
            hyperedges.append((rel_type, pair))
    
    # Add architectural relationships
    architectural_edges = [
        ("uses", ["Trading", "Cairo"]),
        ("runs_on", ["Cairo", "Starknet"]),
        ("implements", ["AstraTrade", "Microservices"]),
        ("uses", ["AstraTrade", "Event_Sourcing"]),
        ("uses", ["Event_Sourcing", "Redis_Streams"]),
        ("follows", ["AstraTrade", "Domain_Driven_Design"]),
        # Cairo-specific relationships
        ("compiles_to", ["Cairo", "Sierra"]),
        ("compiles_to", ["Sierra", "CASM"]),
        ("executes_on", ["CASM", "Cairo_VM"]),
        ("has_type", ["Cairo", "felt252"]),
        ("has_type", ["Starknet", "ContractAddress"]),
        ("manages", ["ContractState", "StoragePointer"]),
        ("uses", ["Cairo", "ownership_system"]),
        ("enforces", ["Cairo", "access_control"]),
        ("validates_with", ["Cairo", "assert"]),
        ("follows", ["Cairo", "CEI_pattern"]),
        ("has_functions", ["Cairo", "constructor"]),
        ("has_functions", ["Cairo", "external"]),
        ("has_functions", ["Cairo", "view"]),
        ("has_functions", ["Cairo", "internal"])
    ]
    
    hyperedges.extend(architectural_edges)
    return hyperedges

def generate_simplified_embeddings(nodes: Set[str], hyperedges: List[Tuple[str, List[str]]]) -> Dict[str, Dict[str, List[float]]]:
    """Generate simplified embeddings for nodes and hyperedges"""
    import random
    random.seed(42)  # For reproducibility
    
    node_embeddings = {}
    edge_embeddings = {}
    
    # Generate node embeddings with some semantic clustering
    for node in nodes:
        # Create slightly different embeddings based on node type/content
        base_val = hash(node) % 100 / 100.0
        embedding = [base_val + random.uniform(-0.1, 0.1) for _ in range(384)]
        node_embeddings[node] = embedding
    
    # Generate edge embeddings
    for edge_type, _ in hyperedges:
        if edge_type not in edge_embeddings:
            base_val = hash(edge_type) % 100 / 100.0
            embedding = [base_val + random.uniform(-0.1, 0.1) for _ in range(384)]
            edge_embeddings[edge_type] = embedding
    
    return {
        "nodes": node_embeddings,
        "hyperedges": edge_embeddings
    }

def get_domain_list(node_types: Dict[str, str]) -> List[str]:
    """Extract list of domains from node types"""
    return [node for node, node_type in node_types.items() if node_type == "domain"]

if __name__ == "__main__":
    build_knowledge_graph()


if __name__ == "__main__":
    build_knowledge_graph()
