#!/usr/bin/env python3
"""
Cairo Expert System - Specialized Sub-Agents for Cairo Development and Security
"""
import json
import pickle
from typing import Dict, List, Any, Optional, Tuple
from abc import ABC, abstractmethod
from enum import Enum
import re

class AgentType(Enum):
    DEVELOPMENT = "cairo_development"
    SECURITY_AUDIT = "cairo_security_audit"
    ARCHITECTURE = "cairo_architecture"
    OPTIMIZATION = "cairo_optimization"

class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class CairoExpertAgent(ABC):
    """Base class for Cairo expert agents"""
    
    def __init__(self, agent_type: AgentType, knowledge_graph: Dict[str, Any]):
        self.agent_type = agent_type
        self.knowledge_graph = knowledge_graph
        self.expertise_areas = self.define_expertise_areas()
        self.confidence_threshold = 0.75  # Require 75% confidence - conservative but reasonable
        self.action_mode = "analysis_only"  # Conservative by default
        
    @abstractmethod
    def define_expertise_areas(self) -> List[str]:
        """Define the areas of expertise for this agent"""
        pass
    
    @abstractmethod
    def can_handle_query(self, query: str) -> Tuple[bool, float]:
        """Determine if this agent can handle the query and confidence level"""
        pass
    
    @abstractmethod
    def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process the query and return structured response"""
        pass
    
    def get_confidence_score(self, query: str) -> float:
        """Calculate confidence score for handling this query"""
        query_lower = query.lower()
        keyword_matches = sum(1 for keyword in self.expertise_areas 
                            if keyword.lower() in query_lower)
        return min(keyword_matches / len(self.expertise_areas), 1.0)
    
    def validate_task_clarity(self, query: str) -> Tuple[bool, List[str]]:
        """Validate if task is clear and specific enough for confident action"""
        unclear_indicators = []
        
        # Check for vague terms
        vague_terms = ["improve", "enhance", "optimize", "fix", "update", "review"]
        for term in vague_terms:
            if term in query.lower() and len(query.split()) < 10:
                unclear_indicators.append(f"Vague request: '{term}' - need specific details")
        
        # Check for missing context
        if any(term in query.lower() for term in ["this", "that", "it"]) and "contract" not in query.lower():
            unclear_indicators.append("Missing context: Which specific contract/file?")
        
        # Check for broad scope
        broad_terms = ["all", "everything", "entire", "whole"]
        if any(term in query.lower() for term in broad_terms):
            unclear_indicators.append("Scope too broad - need specific focus area")
        
        is_clear = len(unclear_indicators) == 0
        return is_clear, unclear_indicators
    
    def require_clarification(self, query: str, unclear_indicators: List[str]) -> Dict[str, Any]:
        """Return clarification request when task is unclear"""
        return {
            "agent": f"{self.agent_type.value.replace('_', ' ').title()} Expert",
            "status": "clarification_needed",
            "confidence": 0.0,
            "original_query": query,
            "unclear_aspects": unclear_indicators,
            "clarification_questions": [
                "Please specify exactly which file/contract needs attention",
                "What specific aspect should be modified (e.g., specific function, security pattern)?",
                "What is the exact change you want made?",
                "Are you looking for analysis only or actual code changes?"
            ],
            "guidance": "I need more specific details to provide confident assistance. Please clarify the above questions."
        }

class CairoDevelopmentAgent(CairoExpertAgent):
    """Specialized agent for Cairo development assistance"""
    
    def __init__(self, knowledge_graph: Dict[str, Any]):
        super().__init__(AgentType.DEVELOPMENT, knowledge_graph)
        self.development_patterns = self.load_development_patterns()
        
    def define_expertise_areas(self) -> List[str]:
        return [
            "function", "constructor", "external", "view", "internal",
            "storage", "struct", "enum", "trait", "impl",
            "interface", "contract", "module", "library",
            "felt252", "array", "map", "dictionary",
            "ownership", "move", "copy", "clone", "drop",
            "starknet", "deployment", "testing", "debugging"
        ]
    
    def can_handle_query(self, query: str) -> Tuple[bool, float]:
        """Determine if this is a development-related query"""
        query_lower = query.lower()
        
        # Development keywords
        dev_keywords = [
            "implement", "write", "create", "develop", "build",
            "function", "contract", "storage", "struct", "interface",
            "how to", "example", "syntax", "pattern", "best practice"
        ]
        
        # Calculate base confidence from development keywords
        dev_score = sum(0.3 for keyword in dev_keywords if keyword in query_lower)
        
        # Boost confidence for specific Cairo development terms
        cairo_dev_terms = ["constructor", "external", "view", "felt252", "starknet", "function", "storage"]
        cairo_score = sum(0.4 for term in cairo_dev_terms if term in query_lower)
        
        confidence = min(dev_score + cairo_score, 1.0)
        
        return confidence > 0.3, confidence
    
    def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process development-related query with enhanced validation"""
        
        # First validate task clarity
        is_clear, unclear_indicators = self.validate_task_clarity(query)
        if not is_clear:
            return self.require_clarification(query, unclear_indicators)
        
        # Check confidence level using the same method as can_handle_query
        can_handle, confidence = self.can_handle_query(query)
        if confidence < self.confidence_threshold:
            return {
                "agent": "Cairo Development Expert",
                "status": "low_confidence",
                "confidence": confidence,
                "query": query,
                "message": f"Confidence level ({confidence:.2f}) below required threshold ({self.confidence_threshold})",
                "recommendation": "Please provide more specific Cairo development details or rephrase the question",
                "alternative": "Try asking about specific function types, storage patterns, or implementation details"
            }
        
        query_lower = query.lower()
        
        # Determine query type with specific focus
        if any(term in query_lower for term in ["function", "constructor", "external", "view"]):
            return self.handle_function_query(query)
        elif any(term in query_lower for term in ["storage", "state", "struct"]):
            return self.handle_storage_query(query)
        elif any(term in query_lower for term in ["interface", "trait", "contract"]):
            return self.handle_interface_query(query)
        elif any(term in query_lower for term in ["testing", "test", "debug"]):
            return self.handle_testing_query(query)
        else:
            return self.handle_general_development_query(query)
    
    def handle_function_query(self, query: str) -> Dict[str, Any]:
        """Handle function-related queries"""
        return {
            "agent": "Cairo Development Expert",
            "query_type": "function_development",
            "guidance": {
                "function_types": {
                    "constructor": {
                        "syntax": "fn constructor(ref self: ContractState, param: Type)",
                        "purpose": "Initialize contract state once during deployment",
                        "example": "fn constructor(ref self: ContractState, owner: ContractAddress) { self.owner.write(owner); }"
                    },
                    "external": {
                        "syntax": "fn function_name(ref self: ContractState, param: Type)",
                        "purpose": "Public functions that can modify state",
                        "example": "fn transfer(ref self: ContractState, to: ContractAddress, amount: u256)"
                    },
                    "view": {
                        "syntax": "fn function_name(self: @ContractState, param: Type) -> ReturnType",
                        "purpose": "Read-only functions for querying state",
                        "example": "fn get_balance(self: @ContractState, account: ContractAddress) -> u256"
                    }
                },
                "best_practices": [
                    "Use assert! for input validation at function start",
                    "Follow naming conventions (snake_case for functions)",
                    "Add comprehensive documentation comments",
                    "Implement proper error handling"
                ]
            },
            "code_examples": self.get_function_examples(),
            "related_concepts": ["storage", "interfaces", "access_control"]
        }
    
    def handle_storage_query(self, query: str) -> Dict[str, Any]:
        """Handle storage-related queries"""
        return {
            "agent": "Cairo Development Expert", 
            "query_type": "storage_development",
            "guidance": {
                "storage_types": {
                    "single_value": {
                        "syntax": "storage_var: StoragePointer<Type>",
                        "operations": ["read()", "write(value)"],
                        "example": "balance: StoragePointer<u256>"
                    },
                    "mapping": {
                        "syntax": "storage_map: Map<KeyType, ValueType>",
                        "operations": ["entry(key).read()", "entry(key).write(value)"],
                        "example": "balances: Map<ContractAddress, u256>"
                    },
                    "complex_types": {
                        "requirement": "Must implement Store trait",
                        "example": "user_data: Map<ContractAddress, UserProfile>"
                    }
                },
                "patterns": {
                    "lazy_storage": "Only store what you need",
                    "gas_optimization": "Pack related data into structs",
                    "access_patterns": "Use appropriate data structures for access patterns"
                }
            },
            "code_examples": self.get_storage_examples(),
            "related_concepts": ["structs", "traits", "gas_optimization"]
        }
    
    def handle_interface_query(self, query: str) -> Dict[str, Any]:
        """Handle interface and contract structure queries"""
        return {
            "agent": "Cairo Development Expert",
            "query_type": "interface_development", 
            "guidance": {
                "interface_definition": {
                    "syntax": "#[starknet::interface]\ntrait IContractName<TContractState>",
                    "purpose": "Define public API for contracts",
                    "example": "trait IERC20<TContractState> { fn transfer(ref self: TContractState, to: ContractAddress, amount: u256); }"
                },
                "contract_structure": {
                    "components": ["interface", "storage", "constructor", "implementation"],
                    "attributes": ["#[starknet::contract]", "#[storage]", "#[constructor]", "#[abi(embed_v0)]"]
                },
                "modularity": {
                    "components": "Use embeddable components for reusability", 
                    "libraries": "Import common functionality from libraries",
                    "inheritance": "Compose contracts through trait implementations"
                }
            },
            "code_examples": self.get_interface_examples(),
            "related_concepts": ["traits", "generics", "modularity"]
        }
    
    def handle_testing_query(self, query: str) -> Dict[str, Any]:
        """Handle testing and debugging queries"""
        return {
            "agent": "Cairo Development Expert",
            "query_type": "testing_development",
            "guidance": {
                "testing_framework": {
                    "cairo_test": "Built-in Cairo testing framework",
                    "starknet_foundry": "Advanced testing and deployment tools",
                    "attributes": ["#[test]", "#[should_panic]", "#[ignore]"]
                },
                "test_patterns": {
                    "unit_tests": "Test individual functions in isolation",
                    "integration_tests": "Test contract interactions",
                    "property_tests": "Test invariants and edge cases"
                },
                "debugging": {
                    "print_debugging": "Use println! for debugging output",
                    "assertion_errors": "Clear error messages with assert!",
                    "gas_profiling": "Monitor gas usage for optimization"
                }
            },
            "code_examples": self.get_testing_examples(),
            "related_concepts": ["deployment", "gas_optimization", "error_handling"]
        }
    
    def handle_general_development_query(self, query: str) -> Dict[str, Any]:
        """Handle general development questions"""
        return {
            "agent": "Cairo Development Expert",
            "query_type": "general_development",
            "guidance": {
                "cairo_fundamentals": {
                    "ownership_system": "Move semantics with explicit Copy/Clone/Drop traits",
                    "type_system": "Strong typing with felt252 as primitive",
                    "memory_safety": "Compile-time memory safety guarantees"
                },
                "development_workflow": {
                    "project_setup": "Use Scarb for package management",
                    "compilation": "Cairo -> Sierra -> CASM compilation pipeline",
                    "deployment": "Deploy to Starknet testnet/mainnet"
                }
            },
            "resources": [
                "Cairo Book: https://book.cairo-lang.org/",
                "Starknet Foundry: https://foundry-rs.github.io/starknet-foundry/",
                "Cairo Core Library: https://docs.cairo-lang.org/core/"
            ],
            "next_steps": ["Set up development environment", "Create first contract", "Write comprehensive tests"]
        }
    
    def load_development_patterns(self) -> Dict[str, Any]:
        """Load common Cairo development patterns"""
        return {
            "access_control": "Owner and role-based patterns",
            "upgradeable_contracts": "Proxy patterns for upgradeability", 
            "event_emission": "Structured logging through events",
            "error_handling": "Assert-based validation and custom errors"
        }
    
    def get_function_examples(self) -> List[str]:
        """Get function implementation examples"""
        return [
            """
// Constructor example
#[constructor]
fn constructor(ref self: ContractState, initial_supply: u256, owner: ContractAddress) {
    assert!(initial_supply > 0, 'Supply must be positive');
    self.total_supply.write(initial_supply);
    self.owner.write(owner);
}
            """,
            """
// External function example  
fn transfer(ref self: ContractState, to: ContractAddress, amount: u256) -> bool {
    let caller = get_caller_address();
    assert!(to != contract_address_const::<0>(), 'Transfer to zero address');
    assert!(amount > 0, 'Amount must be positive');
    
    let sender_balance = self.balances.entry(caller).read();
    assert!(sender_balance >= amount, 'Insufficient balance');
    
    self.balances.entry(caller).write(sender_balance - amount);
    let receiver_balance = self.balances.entry(to).read();
    self.balances.entry(to).write(receiver_balance + amount);
    
    self.emit(Transfer { from: caller, to, amount });
    true
}
            """
        ]
    
    def get_storage_examples(self) -> List[str]:
        """Get storage implementation examples"""
        return [
            """
#[storage]
struct Storage {
    // Single values
    owner: ContractAddress,
    total_supply: u256,
    paused: bool,
    
    // Mappings
    balances: Map<ContractAddress, u256>,
    allowances: Map<(ContractAddress, ContractAddress), u256>,
    
    // Complex types (must implement Store trait)
    user_profiles: Map<ContractAddress, UserProfile>,
}

#[derive(Drop, Serde, starknet::Store)]
struct UserProfile {
    username: felt252,
    reputation: u64,
    created_at: u64,
}
            """
        ]
    
    def get_interface_examples(self) -> List[str]:
        """Get interface implementation examples"""
        return [
            """
#[starknet::interface]
trait IERC20<TContractState> {
    fn name(self: @TContractState) -> ByteArray;
    fn symbol(self: @TContractState) -> ByteArray;
    fn decimals(self: @TContractState) -> u8;
    fn total_supply(self: @TContractState) -> u256;
    fn balance_of(self: @TContractState, account: ContractAddress) -> u256;
    fn allowance(self: @TContractState, owner: ContractAddress, spender: ContractAddress) -> u256;
    fn transfer(ref self: TContractState, to: ContractAddress, amount: u256) -> bool;
    fn transfer_from(ref self: TContractState, from: ContractAddress, to: ContractAddress, amount: u256) -> bool;
    fn approve(ref self: TContractState, spender: ContractAddress, amount: u256) -> bool;
}

#[starknet::contract]
mod ERC20Token {
    use super::IERC20;
    
    #[storage]
    struct Storage {
        name: ByteArray,
        symbol: ByteArray,
        decimals: u8,
        total_supply: u256,
        balances: Map<ContractAddress, u256>,
        allowances: Map<(ContractAddress, ContractAddress), u256>,
    }
    
    #[abi(embed_v0)]
    impl ERC20Impl of IERC20<ContractState> {
        // Implementation here
    }
}
            """
        ]
    
    def get_testing_examples(self) -> List[str]:
        """Get testing implementation examples"""
        return [
            """
#[cfg(test)]
mod tests {
    use super::{ERC20Token, IERC20Dispatcher, IERC20DispatcherTrait};
    use starknet::{ContractAddress, contract_address_const};
    use starknet::testing::{set_caller_address, set_contract_address};

    fn setup() -> (IERC20Dispatcher, ContractAddress) {
        let owner = contract_address_const::<1>();
        let contract = ERC20Token::deploy(1000000, owner);
        let dispatcher = IERC20Dispatcher { contract_address: contract };
        (dispatcher, owner)
    }

    #[test]
    fn test_transfer_success() {
        let (token, owner) = setup();
        let recipient = contract_address_const::<2>();
        
        set_caller_address(owner);
        let success = token.transfer(recipient, 1000);
        
        assert!(success, 'Transfer should succeed');
        assert!(token.balance_of(recipient) == 1000, 'Recipient balance incorrect');
        assert!(token.balance_of(owner) == 999000, 'Owner balance incorrect');
    }

    #[test]
    #[should_panic(expected: 'Insufficient balance')]
    fn test_transfer_insufficient_balance() {
        let (token, _) = setup();
        let poor_user = contract_address_const::<3>();
        
        set_caller_address(poor_user);
        token.transfer(contract_address_const::<4>(), 1000);
    }
}
            """
        ]

class CairoSecurityAuditAgent(CairoExpertAgent):
    """Specialized agent for Cairo security auditing"""
    
    def __init__(self, knowledge_graph: Dict[str, Any]):
        super().__init__(AgentType.SECURITY_AUDIT, knowledge_graph)
        self.vulnerability_database = self.load_vulnerability_database()
        self.security_patterns = self.load_security_patterns()
        
    def define_expertise_areas(self) -> List[str]:
        return [
            "security", "audit", "vulnerability", "exploit",
            "access_control", "authorization", "authentication",
            "reentrancy", "overflow", "underflow", "validation",
            "assert", "panic", "error_handling",
            "privileges", "roles", "ownership",
            "input_validation", "sanitization", "bounds_checking"
        ]
    
    def can_handle_query(self, query: str) -> Tuple[bool, float]:
        """Determine if this is a security-related query"""
        query_lower = query.lower()
        
        # Security keywords
        security_keywords = [
            "security", "audit", "vulnerability", "exploit", "attack",
            "secure", "safe", "validation", "access", "permission",
            "role", "owner", "authorization", "authentication"
        ]
        
        # Calculate base confidence from security keywords
        security_score = sum(0.3 for keyword in security_keywords if keyword in query_lower)
        
        # Boost confidence for specific security terms
        security_terms = ["assert", "access_control", "reentrancy", "overflow", "validation", "vulnerability"]
        specific_score = sum(0.4 for term in security_terms if term in query_lower)
        
        confidence = min(security_score + specific_score, 1.0)
        
        return confidence > 0.2, confidence
    
    def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process security-related query with enhanced validation"""
        
        # First validate task clarity
        is_clear, unclear_indicators = self.validate_task_clarity(query)
        if not is_clear:
            return self.require_clarification(query, unclear_indicators)
        
        # Check confidence level using the same method as can_handle_query
        can_handle, confidence = self.can_handle_query(query)
        if confidence < self.confidence_threshold:
            return {
                "agent": "Cairo Security Audit Expert",
                "status": "low_confidence",
                "confidence": confidence,
                "query": query,
                "message": f"Confidence level ({confidence:.2f}) below required threshold ({self.confidence_threshold})",
                "recommendation": "Please provide more specific security concerns or vulnerabilities to analyze",
                "alternative": "Try asking about specific security patterns like access control, input validation, or vulnerability types"
            }
        
        query_lower = query.lower()
        
        # Determine query type with specific focus
        if any(term in query_lower for term in ["access", "control", "permission", "role", "owner"]):
            return self.handle_access_control_query(query)
        elif any(term in query_lower for term in ["validation", "input", "assert", "sanitize"]):
            return self.handle_input_validation_query(query)
        elif any(term in query_lower for term in ["reentrancy", "attack", "exploit"]):
            return self.handle_vulnerability_query(query)
        elif any(term in query_lower for term in ["audit", "review", "check"]):
            return self.handle_audit_query(query)
        else:
            return self.handle_general_security_query(query)
    
    def handle_access_control_query(self, query: str) -> Dict[str, Any]:
        """Handle access control security queries"""
        return {
            "agent": "Cairo Security Audit Expert",
            "query_type": "access_control_security",
            "security_analysis": {
                "owner_pattern": {
                    "implementation": {
                        "storage": "owner: ContractAddress",
                        "validation": "assert!(get_caller_address() == self.owner.read(), 'Not owner');"
                    },
                    "vulnerabilities": [
                        "Unprotected owner transfer functions",
                        "Missing owner validation in critical functions",
                        "Hardcoded owner addresses"
                    ],
                    "mitigations": [
                        "Implement two-step ownership transfer",
                        "Add owner validation to all privileged functions",
                        "Use role-based access for granular permissions"
                    ]
                },
                "role_based_access": {
                    "implementation": {
                        "storage": "roles: Map<ContractAddress, felt252>",
                        "validation": "assert!(self.has_role(required_role), 'Missing role');"
                    },
                    "best_practices": [
                        "Use constants for role identifiers",
                        "Implement role granting/revoking functions",
                        "Add role hierarchy if needed"
                    ]
                }
            },
            "code_examples": self.get_access_control_examples(),
            "audit_checklist": [
                "Verify all privileged functions have access control",
                "Check for privilege escalation vulnerabilities", 
                "Validate role assignment mechanisms",
                "Test unauthorized access scenarios"
            ]
        }
    
    def handle_input_validation_query(self, query: str) -> Dict[str, Any]:
        """Handle input validation security queries"""
        return {
            "agent": "Cairo Security Audit Expert",
            "query_type": "input_validation_security",
            "security_analysis": {
                "validation_patterns": {
                    "parameter_validation": {
                        "technique": "Early validation with assert!",
                        "example": "assert!(amount > 0, 'Amount must be positive');"
                    },
                    "address_validation": {
                        "technique": "Zero address checking",
                        "example": "assert!(to != contract_address_const::<0>(), 'Invalid address');"
                    },
                    "bounds_checking": {
                        "technique": "Range validation",
                        "example": "assert!(index < array.len(), 'Index out of bounds');"
                    }
                },
                "common_vulnerabilities": [
                    "Missing input validation leading to unexpected behavior",
                    "Integer overflow/underflow in calculations",
                    "Array bounds violations",
                    "Null/zero address interactions"
                ],
                "prevention_strategies": [
                    "Validate all external inputs at function entry",
                    "Use appropriate data types for value ranges",
                    "Implement comprehensive error messages",
                    "Test edge cases and boundary conditions"
                ]
            },
            "code_examples": self.get_input_validation_examples(),
            "audit_checklist": [
                "Check all external function parameters are validated",
                "Verify array access bounds checking",
                "Test with invalid/malicious inputs",
                "Validate error handling and recovery"
            ]
        }
    
    def handle_vulnerability_query(self, query: str) -> Dict[str, Any]:
        """Handle specific vulnerability queries"""
        return {
            "agent": "Cairo Security Audit Expert", 
            "query_type": "vulnerability_analysis",
            "security_analysis": {
                "reentrancy": {
                    "risk_level": "Medium on Starknet",
                    "description": "External contract calls that can re-enter current contract",
                    "prevention": "Follow Checks-Effects-Interactions (CEI) pattern",
                    "example": "Update state before external calls"
                },
                "integer_issues": {
                    "risk_level": "Low in Cairo",
                    "description": "Cairo provides built-in overflow protection",
                    "note": "felt252 uses modular arithmetic",
                    "prevention": "Use appropriate integer types for value ranges"
                },
                "access_control_bypass": {
                    "risk_level": "High",
                    "description": "Unauthorized access to privileged functions",
                    "prevention": "Implement proper role validation in all functions"
                }
            },
            "cei_pattern": {
                "checks": "Validate all conditions and inputs",
                "effects": "Update contract state",
                "interactions": "Call external contracts last"
            },
            "code_examples": self.get_vulnerability_prevention_examples(),
            "audit_checklist": [
                "Verify CEI pattern implementation",
                "Check for privilege escalation paths",
                "Test state consistency after external calls",
                "Validate error handling in edge cases"
            ]
        }
    
    def handle_audit_query(self, query: str) -> Dict[str, Any]:
        """Handle security audit process queries"""
        return {
            "agent": "Cairo Security Audit Expert",
            "query_type": "security_audit_process",
            "audit_methodology": {
                "phases": {
                    "1_preparation": {
                        "activities": ["Understand business logic", "Review documentation", "Set up testing environment"],
                        "deliverables": ["Audit scope", "Test plan", "Environment setup"]
                    },
                    "2_static_analysis": {
                        "activities": ["Code review", "Pattern analysis", "Vulnerability scanning"],
                        "tools": ["Manual review", "Static analyzers", "Custom scripts"]
                    },
                    "3_dynamic_testing": {
                        "activities": ["Unit testing", "Integration testing", "Attack simulation"],
                        "focus": ["Edge cases", "Error conditions", "Malicious inputs"]
                    },
                    "4_reporting": {
                        "deliverables": ["Vulnerability report", "Risk assessment", "Remediation recommendations"],
                        "severity_levels": ["Critical", "High", "Medium", "Low", "Informational"]
                    }
                }
            },
            "audit_checklist": self.get_comprehensive_audit_checklist(),
            "tools_and_techniques": [
                "Manual code review for logic flaws",
                "Automated testing with edge cases",
                "Gas optimization analysis",
                "Access control verification"
            ]
        }
    
    def handle_general_security_query(self, query: str) -> Dict[str, Any]:
        """Handle general security questions"""
        return {
            "agent": "Cairo Security Audit Expert",
            "query_type": "general_security",
            "security_principles": {
                "defense_in_depth": "Multiple layers of security controls",
                "least_privilege": "Minimal necessary permissions",
                "fail_secure": "Secure defaults and error handling",
                "separation_of_concerns": "Modular security implementations"
            },
            "cairo_security_features": {
                "ownership_system": "Memory safety and resource management",
                "type_system": "Strong typing prevents many vulnerabilities",
                "compilation": "Compile-time checks catch errors early"
            },
            "best_practices": [
                "Implement comprehensive input validation",
                "Use role-based access control appropriately",
                "Follow secure development lifecycle",
                "Conduct regular security audits"
            ]
        }
    
    def load_vulnerability_database(self) -> Dict[str, Any]:
        """Load vulnerability patterns and signatures"""
        return {
            "access_control": {
                "missing_auth": "Functions without caller validation",
                "privilege_escalation": "Incorrect role assignment logic",
                "hardcoded_access": "Hardcoded privileged addresses"
            },
            "input_validation": {
                "missing_validation": "No input parameter checking",
                "bounds_errors": "Array/map access without bounds checking",
                "type_confusion": "Incorrect type casting or assumptions"
            }
        }
    
    def load_security_patterns(self) -> Dict[str, Any]:
        """Load security implementation patterns"""
        return {
            "access_control_patterns": ["owner", "role_based", "multi_sig"],
            "validation_patterns": ["early_validation", "sanitization", "bounds_checking"],
            "architectural_patterns": ["cei", "separation_of_concerns", "fail_secure"]
        }
    
    def get_access_control_examples(self) -> List[str]:
        """Get access control implementation examples"""
        return [
            """
// Owner pattern implementation
#[storage]
struct Storage {
    owner: ContractAddress,
}

#[generate_trait]
impl AccessControl of AccessControlTrait {
    fn only_owner(self: @ContractState) {
        assert!(get_caller_address() == self.owner.read(), 'Not owner');
    }
    
    fn transfer_ownership(ref self: ContractState, new_owner: ContractAddress) {
        self.only_owner();
        assert!(new_owner != contract_address_const::<0>(), 'Invalid new owner');
        
        let old_owner = self.owner.read();
        self.owner.write(new_owner);
        self.emit(OwnershipTransferred { previous_owner: old_owner, new_owner });
    }
}
            """,
            """
// Role-based access control
#[storage]
struct Storage {
    roles: Map<(ContractAddress, felt252), bool>,
    role_admin: Map<felt252, felt252>,
}

const ADMIN_ROLE: felt252 = 'ADMIN_ROLE';
const MINTER_ROLE: felt252 = 'MINTER_ROLE';

#[generate_trait]
impl RoleBasedAccess of RoleBasedAccessTrait {
    fn has_role(self: @ContractState, role: felt252, account: ContractAddress) -> bool {
        self.roles.entry((account, role)).read()
    }
    
    fn require_role(self: @ContractState, role: felt252) {
        assert!(self.has_role(role, get_caller_address()), 'Missing required role');
    }
    
    fn grant_role(ref self: ContractState, role: felt252, account: ContractAddress) {
        let admin_role = self.role_admin.entry(role).read();
        self.require_role(admin_role);
        
        self.roles.entry((account, role)).write(true);
        self.emit(RoleGranted { role, account, sender: get_caller_address() });
    }
}
            """
        ]
    
    def get_input_validation_examples(self) -> List[str]:
        """Get input validation examples"""
        return [
            """
// Comprehensive input validation
fn transfer(ref self: ContractState, to: ContractAddress, amount: u256) -> bool {
    // Validate inputs early
    assert!(to != contract_address_const::<0>(), 'Transfer to zero address');
    assert!(amount > 0, 'Amount must be positive');
    assert!(amount <= MAX_TRANSFER_AMOUNT, 'Amount exceeds maximum');
    
    let from = get_caller_address();
    assert!(from != to, 'Cannot transfer to self');
    
    // Validate state conditions
    let sender_balance = self.balances.entry(from).read();
    assert!(sender_balance >= amount, 'Insufficient balance');
    
    // Execute transfer logic
    self._transfer(from, to, amount)
}

// Array access with bounds checking
fn get_user_at_index(self: @ContractState, index: u32) -> ContractAddress {
    let user_count = self.user_count.read();
    assert!(index < user_count, 'Index out of bounds');
    
    self.users.entry(index).read()
}
            """
        ]
    
    def get_vulnerability_prevention_examples(self) -> List[str]:
        """Get vulnerability prevention examples"""
        return [
            """
// CEI Pattern Implementation
fn withdraw(ref self: ContractState, amount: u256) {
    let caller = get_caller_address();
    
    // CHECKS: Validate all conditions
    assert!(amount > 0, 'Amount must be positive');
    let balance = self.balances.entry(caller).read();
    assert!(balance >= amount, 'Insufficient balance');
    assert!(!self.paused.read(), 'Contract is paused');
    
    // EFFECTS: Update contract state
    self.balances.entry(caller).write(balance - amount);
    let total_withdrawn = self.total_withdrawn.read();
    self.total_withdrawn.write(total_withdrawn + amount);
    
    // INTERACTIONS: External calls last
    self.emit(Withdrawal { user: caller, amount });
    // External token transfer would go here
}

// Reentrancy protection pattern
#[storage]
struct Storage {
    reentrancy_guard: bool,
}

fn protected_function(ref self: ContractState) {
    assert!(!self.reentrancy_guard.read(), 'Reentrant call');
    self.reentrancy_guard.write(true);
    
    // Function logic here
    
    self.reentrancy_guard.write(false);
}
            """
        ]
    
    def get_comprehensive_audit_checklist(self) -> Dict[str, List[str]]:
        """Get comprehensive security audit checklist"""
        return {
            "architecture_review": [
                "Verify separation of concerns in contract design",
                "Check upgrade mechanisms and proxy patterns",
                "Validate access control architecture",
                "Review state management and data flow"
            ],
            "access_control": [
                "Verify all privileged functions have proper access control",
                "Check for privilege escalation vulnerabilities",
                "Validate role assignment and revocation mechanisms",
                "Test unauthorized access scenarios"
            ],
            "input_validation": [
                "Check all external inputs are validated",
                "Verify bounds checking for arrays and maps",
                "Test with malicious and edge case inputs",
                "Validate error handling and recovery"
            ],
            "state_management": [
                "Verify atomic state transitions",
                "Check for state corruption vulnerabilities",
                "Validate invariant preservation",
                "Test concurrent access scenarios"
            ],
            "external_interactions": [
                "Verify CEI pattern implementation",
                "Check return value handling",
                "Test reentrancy protection",
                "Validate external call failure handling"
            ],
            "gas_and_dos": [
                "Check for gas limit DOS vulnerabilities",
                "Verify loop bounds and termination",
                "Test resource exhaustion scenarios",
                "Validate gas optimization practices"
            ]
        }

class CairoExpertCoordinator:
    """Coordinates multiple Cairo expert agents"""
    
    def __init__(self, knowledge_graph: Dict[str, Any]):
        self.knowledge_graph = knowledge_graph
        self.agents = {
            AgentType.DEVELOPMENT: CairoDevelopmentAgent(knowledge_graph),
            AgentType.SECURITY_AUDIT: CairoSecurityAuditAgent(knowledge_graph)
        }
        
    def route_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Route query to most appropriate specialist agent with enhanced validation"""
        
        # Validate query specificity first
        if len(query.strip()) < 10:
            return {
                "status": "query_too_short",
                "message": "Query too brief for confident analysis",
                "guidance": "Please provide more detailed question (at least 10 characters)",
                "confidence": 0.0
            }
        
        best_agent = None
        best_confidence = 0.0
        
        # Get confidence scores from all agents
        agent_scores = {}
        for agent_type, agent in self.agents.items():
            can_handle, confidence = agent.can_handle_query(query)
            agent_scores[agent_type] = confidence
            
            if can_handle and confidence > best_confidence:
                best_confidence = confidence
                best_agent = agent
        
        # Require reasonable confidence for routing
        if best_confidence < 0.5:
            return {
                "status": "uncertain_routing",
                "message": f"Unable to route with high confidence (best: {best_confidence:.2f})",
                "agent_scores": {k.value: v for k, v in agent_scores.items()},
                "guidance": "Please be more specific about whether this is a development or security question",
                "suggestions": [
                    "For code implementation questions, mention 'function', 'storage', or 'contract'",
                    "For security questions, mention 'vulnerability', 'access control', or 'audit'"
                ]
            }
        
        # Process query with selected agent
        response = best_agent.process_query(query, context)
        
        # Add routing metadata
        response["routing_info"] = {
            "selected_agent": best_agent.agent_type.value,
            "confidence": best_confidence,
            "agent_scores": {k.value: v for k, v in agent_scores.items()},
            "routing_method": "high_confidence_routing"
        }
        
        return response
    
    def get_specialized_guidance(self, domain: str, query: str) -> Dict[str, Any]:
        """Get guidance from specific domain expert"""
        if domain == "development":
            agent = self.agents[AgentType.DEVELOPMENT]
        elif domain == "security":
            agent = self.agents[AgentType.SECURITY_AUDIT]
        else:
            return {"error": f"Unknown domain: {domain}"}
        
        return agent.process_query(query)
    
    def collaborative_analysis(self, query: str) -> Dict[str, Any]:
        """Get analysis from multiple agents for comprehensive coverage"""
        results = {}
        
        for agent_type, agent in self.agents.items():
            can_handle, confidence = agent.can_handle_query(query)
            if can_handle and confidence > 0.3:
                results[agent_type.value] = agent.process_query(query)
        
        return {
            "collaborative_analysis": True,
            "query": query,
            "agent_responses": results,
            "synthesis": self.synthesize_responses(results)
        }
    
    def synthesize_responses(self, responses: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize responses from multiple agents"""
        synthesis = {
            "key_insights": [],
            "recommendations": [],
            "priority_actions": []
        }
        
        for agent_type, response in responses.items():
            # Extract key insights
            if "guidance" in response:
                synthesis["key_insights"].append(f"{agent_type}: {list(response['guidance'].keys())}")
            
            # Extract recommendations
            if "best_practices" in response.get("guidance", {}):
                synthesis["recommendations"].extend(response["guidance"]["best_practices"])
            
            if "audit_checklist" in response:
                synthesis["priority_actions"].extend(response["audit_checklist"][:3])
        
        return synthesis