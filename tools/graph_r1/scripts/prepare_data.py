import json
import re
import os
import ast
from pathlib import Path
from typing import Dict, List, Any, Set

def prepare_data():
    print("Processing AstraTrade codebase data...")
    
    project_root = "/Users/admin/AstraTrade-Submission"
    processed_data = []
    
    # Analyze different parts of the codebase
    processed_data.extend(analyze_python_domains(project_root))
    processed_data.extend(analyze_cairo_contracts(project_root))
    processed_data.extend(analyze_architecture_docs(project_root))
    processed_data.extend(analyze_services(project_root))
    
    # Add Cairo language knowledge
    processed_data.extend(load_cairo_knowledge())
    
    print(f"Processed {len(processed_data)} items from AstraTrade codebase and Cairo knowledge.")
    
    with open("/Users/admin/AstraTrade-Submission/graph_r1/data/cairo_book_processed.json", "w") as f:
        json.dump(processed_data, f, indent=4)
    
    print("Saved processed AstraTrade data to data/cairo_book_processed.json")

def load_cairo_knowledge() -> List[Dict[str, Any]]:
    """Load Cairo language knowledge base"""
    cairo_kb_path = "/Users/admin/AstraTrade-Submission/graph_r1/data/cairo_knowledge_base.json"
    
    try:
        with open(cairo_kb_path, 'r') as f:
            cairo_kb = json.load(f)
    except FileNotFoundError:
        print("Cairo knowledge base not found, skipping...")
        return []
    
    processed_cairo = []
    
    # Process Cairo fundamentals
    for topic, content in cairo_kb.items():
        if isinstance(content, dict):
            for subtopic, details in content.items():
                question = f"What is {subtopic.replace('_', ' ')} in Cairo?"
                answer = f"Cairo {topic}: {subtopic}"
                supporting_fact = f"Topic: {topic} | Subtopic: {subtopic} | Details: {json.dumps(details)[:200]}"
                
                processed_cairo.append({
                    "question": question,
                    "answer": answer,
                    "supporting_facts": [supporting_fact]
                })
    
    # Add specific Cairo security knowledge
    security_items = [
        {
            "question": "What are Cairo smart contract security best practices?",
            "answer": "Cairo Security: Access control, input validation, CEI pattern",
            "supporting_facts": ["Security patterns: Access control with role-based permissions, Input validation using assert! macros, Checks-Effects-Interactions pattern, Integer overflow protection built-in"]
        },
        {
            "question": "How to implement access control in Cairo contracts?",
            "answer": "Cairo Access Control: Owner pattern, role mappings, guard functions",
            "supporting_facts": ["Access control implementation: Use Map<ContractAddress, bool> for roles, Implement guard functions with assert!, Example: fn only_owner(self: @ContractState) { assert!(self.is_owner(), 'Not owner'); }"]
        },
        {
            "question": "What are Cairo contract function types?",
            "answer": "Cairo Functions: Constructor, external, view, internal functions",
            "supporting_facts": ["Function types: Constructor (ref self, runs once), External (ref self, mutable), View (self: @ContractState, read-only), Internal (private, no ABI export)"]
        },
        {
            "question": "How to audit Cairo smart contracts?",
            "answer": "Cairo Audit: Architecture review, code quality, security checks, testing",
            "supporting_facts": ["Audit checklist: Architecture (separation of concerns, upgrade security), Code quality (error handling, validation), Security (privilege escalation, reentrancy), Testing (unit tests, edge cases)"]
        }
    ]
    
    processed_cairo.extend(security_items)
    
    return processed_cairo

def analyze_python_domains(project_root: str) -> List[Dict[str, Any]]:
    """Analyze Python domain structure in apps/backend/domains/"""
    data = []
    domains_path = Path(project_root) / "apps" / "backend" / "domains"
    
    if not domains_path.exists():
        return data
    
    for domain_dir in domains_path.iterdir():
        if domain_dir.is_dir() and not domain_dir.name.startswith('.'):
            domain_info = extract_domain_info(domain_dir)
            if domain_info:
                data.append({
                    "question": f"What is the {domain_dir.name} domain structure?",
                    "answer": f"Domain: {domain_dir.name}",
                    "supporting_facts": [domain_info]
                })
    
    return data

def extract_domain_info(domain_path: Path) -> str:
    """Extract information from a domain directory"""
    info_parts = [f"Domain: {domain_path.name}"]
    
    # Look for key files
    key_files = ['entities.py', 'services.py', 'events.py', 'repositories.py']
    for file_name in key_files:
        file_path = domain_path / file_name
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    classes = extract_python_classes(content)
                    if classes:
                        info_parts.append(f"{file_name}: {', '.join(classes)}")
            except Exception as e:
                continue
    
    return " | ".join(info_parts)

def extract_python_classes(content: str) -> List[str]:
    """Extract class names from Python code"""
    classes = []
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
    except:
        # Fallback to regex if AST parsing fails
        classes = re.findall(r'^class\s+(\w+)', content, re.MULTILINE)
    return classes

def analyze_cairo_contracts(project_root: str) -> List[Dict[str, Any]]:
    """Analyze Cairo smart contracts"""
    data = []
    contracts_path = Path(project_root) / "src" / "contracts"
    
    if not contracts_path.exists():
        return data
    
    for cairo_file in contracts_path.glob("*.cairo"):
        try:
            with open(cairo_file, 'r') as f:
                content = f.read()
                contract_info = extract_cairo_info(content, cairo_file.name)
                if contract_info:
                    data.append({
                        "question": f"What does the {cairo_file.stem} contract do?",
                        "answer": f"Cairo contract: {cairo_file.stem}",
                        "supporting_facts": [contract_info]
                    })
        except Exception as e:
            continue
    
    return data

def extract_cairo_info(content: str, filename: str) -> str:
    """Extract information from Cairo contract"""
    info_parts = [f"Contract: {filename}"]
    
    # Extract interfaces and functions
    interfaces = re.findall(r'#\[starknet::interface\]\s*trait\s+(\w+)', content)
    functions = re.findall(r'fn\s+(\w+)', content)
    
    if interfaces:
        info_parts.append(f"Interfaces: {', '.join(interfaces)}")
    if functions:
        info_parts.append(f"Functions: {', '.join(functions[:5])}")  # Limit to first 5
    
    return " | ".join(info_parts)

def analyze_architecture_docs(project_root: str) -> List[Dict[str, Any]]:
    """Analyze architecture documentation"""
    data = []
    docs_paths = [
        Path(project_root) / "docs",
        Path(project_root)
    ]
    
    for docs_path in docs_paths:
        if docs_path.exists():
            for md_file in docs_path.glob("**/*.md"):
                if md_file.name.upper().startswith(('ARCH', 'TECH', 'PHASE', 'SECURITY')):
                    try:
                        with open(md_file, 'r') as f:
                            content = f.read()[:1000]  # First 1000 chars
                            data.append({
                                "question": f"What is described in {md_file.name}?",
                                "answer": f"Architecture doc: {md_file.name}",
                                "supporting_facts": [content]
                            })
                    except Exception:
                        continue
    
    return data

def analyze_services(project_root: str) -> List[Dict[str, Any]]:
    """Analyze microservices structure"""
    data = []
    services_path = Path(project_root) / "apps" / "backend" / "services"
    
    if not services_path.exists():
        return data
    
    for service_dir in services_path.iterdir():
        if service_dir.is_dir() and not service_dir.name.startswith('.'):
            service_files = list(service_dir.glob("*.py"))
            if service_files:
                data.append({
                    "question": f"What is the {service_dir.name} service?",
                    "answer": f"Microservice: {service_dir.name}",
                    "supporting_facts": [f"Service: {service_dir.name} | Files: {', '.join([f.name for f in service_files[:3]])}"]
                })
    
    return data

if __name__ == "__main__":
    prepare_data()
