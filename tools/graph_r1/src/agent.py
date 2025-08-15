import torch
import pickle
import json
from typing import Dict, List, Any, Tuple
import re

class Agent(torch.nn.Module):
    def __init__(self):
        super(Agent, self).__init__()
        # The original code, which loads the large Qwen2 model, is commented out.
        # self.tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2-1.5B-Instruct")
        # self.policy_model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2-1.5B-Instruct")
        
        # Load enhanced knowledge graph
        self.knowledge_graph = self.load_knowledge_graph()
        self.processed_data = self.load_processed_data()
        print("Initialized ENHANCED Agent with AstraTrade knowledge graph.")

    def load_knowledge_graph(self) -> Dict[str, Any]:
        """Load the enhanced knowledge graph"""
        try:
            with open("/Users/admin/AstraTrade-Submission/graph_r1/data/knowledge_hypergraph.pickle", "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            print("Knowledge graph not found. Please run 'init' first.")
            return {"nodes": [], "hyperedges": [], "embeddings": {}}

    def load_processed_data(self) -> List[Dict[str, Any]]:
        """Load processed AstraTrade data"""
        try:
            with open("/Users/admin/AstraTrade-Submission/graph_r1/data/cairo_book_processed.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print("Processed data not found. Please run 'init' first.")
            return []

    def forward(self, state):
        # Enhanced query processing based on knowledge graph
        query = self.extract_query_from_state(state)
        return self.process_query(query)

    def extract_query_from_state(self, state: str) -> str:
        """Extract meaningful query from state"""
        # Simple extraction - in full implementation this would be more sophisticated
        return state if isinstance(state, str) else "What is AstraTrade?"

    def process_query(self, query: str) -> str:
        """Process query using enhanced knowledge graph"""
        query_lower = query.lower()
        
        # Query routing based on content
        if any(term in query_lower for term in ["domain", "architecture", "structure"]):
            return self.handle_architecture_query(query)
        elif any(term in query_lower for term in ["cairo", "contract", "smart"]):
            return self.handle_cairo_query(query)
        elif any(term in query_lower for term in ["service", "microservice"]):
            return self.handle_service_query(query)
        elif any(term in query_lower for term in ["trading", "gamification", "financial"]):
            return self.handle_domain_query(query)
        else:
            return self.handle_general_query(query)

    def handle_architecture_query(self, query: str) -> str:
        """Handle architecture-related queries"""
        domains = self.knowledge_graph.get("metadata", {}).get("domains", [])
        node_types = self.knowledge_graph.get("node_types", {})
        
        architecture_nodes = [node for node, node_type in node_types.items() 
                            if node_type in ["domain", "architecture", "pattern"]]
        
        response = f"<query>AstraTrade Architecture: {', '.join(domains)} domains with {', '.join(architecture_nodes[:5])} patterns</query>"
        return response

    def handle_cairo_query(self, query: str) -> str:
        """Handle Cairo/smart contract queries with enhanced knowledge"""
        node_types = self.knowledge_graph.get("node_types", {})
        
        # Get Cairo-specific nodes
        cairo_nodes = [node for node, node_type in node_types.items() 
                      if node_type in ["cairo_contract", "function", "programming_language", 
                                      "cairo_data_type", "starknet_type", "cairo_security_pattern"]]
        
        # Find relevant Cairo information from processed data
        cairo_info = []
        security_info = []
        
        for item in self.processed_data:
            answer = item.get("answer", "").lower()
            if "cairo" in answer:
                if "security" in answer or "audit" in answer:
                    security_info.extend(item.get("supporting_facts", []))
                else:
                    cairo_info.extend(item.get("supporting_facts", []))
        
        # Determine query type and provide specific guidance
        query_lower = query.lower()
        
        if any(term in query_lower for term in ["security", "audit", "vulnerability", "safe"]):
            relevant_info = security_info[0][:150] if security_info else "Cairo security: Access control patterns, input validation with assert!, CEI pattern"
            response = f"<query>Cairo Security: {', '.join([n for n in cairo_nodes if 'security' in node_types.get(n, '') or 'pattern' in node_types.get(n, '')])[:3]} | {relevant_info}</query>"
        
        elif any(term in query_lower for term in ["function", "constructor", "external", "view"]):
            relevant_info = "Function types: Constructor (initialization), External (state changes), View (read-only), Internal (private)"
            response = f"<query>Cairo Functions: constructor, external, view, internal | {relevant_info}</query>"
        
        elif any(term in query_lower for term in ["storage", "state", "data"]):
            relevant_info = "Storage: ContractState, StoragePointer, Map collections, felt252 primitive type"
            response = f"<query>Cairo Storage: ContractState, StoragePointer, Map, felt252 | {relevant_info}</query>"
        
        else:
            relevant_info = cairo_info[0][:150] if cairo_info else "Cairo: Safe programming language for Starknet smart contracts with ownership system"
            response = f"<query>Cairo: {', '.join(cairo_nodes[:3])} | {relevant_info}</query>"
        
        return response

    def handle_service_query(self, query: str) -> str:
        """Handle microservice queries"""
        node_types = self.knowledge_graph.get("node_types", {})
        services = [node for node, node_type in node_types.items() 
                   if node_type in ["microservice", "service"]]
        
        response = f"<query>AstraTrade Services: {', '.join(services[:5])}</query>"
        return response

    def handle_domain_query(self, query: str) -> str:
        """Handle domain-specific queries"""
        domains = self.knowledge_graph.get("metadata", {}).get("domains", [])
        
        # Find domain-specific information
        domain_info = []
        for item in self.processed_data:
            answer = item.get("answer", "")
            if any(domain.lower() in answer.lower() for domain in domains):
                domain_info.extend(item.get("supporting_facts", []))
        
        response = f"<query>AstraTrade Domains: {', '.join(domains)} | {domain_info[0][:100] if domain_info else 'Trading, Gamification, Financial domains'}</query>"
        return response

    def handle_general_query(self, query: str) -> str:
        """Handle general queries about AstraTrade"""
        total_nodes = self.knowledge_graph.get("metadata", {}).get("total_nodes", 0)
        total_edges = self.knowledge_graph.get("metadata", {}).get("total_edges", 0)
        
        response = f"<query>AstraTrade platform with {total_nodes} components, {total_edges} relationships, microservices architecture on Starknet</query>"
        return response

    def query_knowledge_graph(self, concept: str) -> List[str]:
        """Query the knowledge graph for related concepts"""
        related = []
        hyperedges = self.knowledge_graph.get("hyperedges", [])
        
        for edge_type, nodes in hyperedges:
            if concept in nodes:
                related.extend([n for n in nodes if n != concept])
        
        return list(set(related))[:5]  # Return top 5 related concepts
