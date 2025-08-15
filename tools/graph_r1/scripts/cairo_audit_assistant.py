#!/usr/bin/env python3
"""
Cairo Smart Contract Audit Assistant
Provides specialized Cairo security analysis and audit guidance
"""
import json
import re
from typing import Dict, List, Any, Tuple
from pathlib import Path

class CairoAuditAssistant:
    def __init__(self):
        self.security_patterns = self.load_security_patterns()
        self.vulnerability_checklist = self.load_vulnerability_checklist()
        
    def load_security_patterns(self) -> Dict[str, Any]:
        """Load Cairo security patterns"""
        return {
            "access_control": {
                "owner_pattern": {
                    "implementation": "single_privileged_address",
                    "example": "owner: ContractAddress",
                    "validation": "assert!(self.owner.read() == get_caller_address(), 'Not owner');"
                },
                "role_based": {
                    "implementation": "role_mapping",
                    "example": "roles: Map<ContractAddress, felt252>",
                    "validation": "assert!(self.has_role(role), 'Missing role');"
                }
            },
            "input_validation": {
                "assert_macro": {
                    "purpose": "condition_validation",
                    "example": "assert!(amount > 0, 'Invalid amount');",
                    "best_practice": "early_validation"
                },
                "panic_macro": {
                    "purpose": "error_termination",
                    "example": "panic!('Critical error');",
                    "usage": "unrecoverable_errors"
                }
            },
            "cei_pattern": {
                "checks": "validate_all_conditions",
                "effects": "update_contract_state", 
                "interactions": "external_contract_calls",
                "purpose": "prevent_reentrancy"
            }
        }
    
    def load_vulnerability_checklist(self) -> Dict[str, List[str]]:
        """Load Cairo vulnerability checklist"""
        return {
            "access_control": [
                "proper_owner_validation",
                "role_assignment_protection",
                "privilege_escalation_prevention",
                "function_visibility_correctness"
            ],
            "input_validation": [
                "parameter_bounds_checking",
                "null_address_validation", 
                "overflow_underflow_protection",
                "array_bounds_validation"
            ],
            "state_management": [
                "storage_consistency",
                "atomic_operations",
                "state_transition_validation",
                "invariant_preservation"
            ],
            "external_calls": [
                "reentrancy_protection",
                "return_value_handling",
                "gas_limit_considerations",
                "call_data_validation"
            ]
        }
    
    def analyze_contract_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a Cairo contract file for security issues"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
        except FileNotFoundError:
            return {"error": "File not found"}
        
        analysis = {
            "file": file_path,
            "contract_structure": self.analyze_contract_structure(content),
            "security_issues": self.identify_security_issues(content),
            "recommendations": self.generate_recommendations(content),
            "audit_score": 0
        }
        
        # Calculate audit score
        analysis["audit_score"] = self.calculate_audit_score(analysis)
        
        return analysis
    
    def analyze_contract_structure(self, content: str) -> Dict[str, Any]:
        """Analyze the structure of a Cairo contract"""
        structure = {
            "has_interface": bool(re.search(r'#\[starknet::interface\]', content)),
            "has_constructor": bool(re.search(r'#\[constructor\]', content)),
            "has_storage": bool(re.search(r'#\[storage\]', content)),
            "function_types": {
                "external": len(re.findall(r'ref self: ContractState', content)),
                "view": len(re.findall(r'self: @ContractState', content)),
                "internal": len(re.findall(r'fn _\w+', content))
            },
            "imports": re.findall(r'use\s+([^;]+);', content),
            "events": len(re.findall(r'#\[event\]', content))
        }
        
        return structure
    
    def identify_security_issues(self, content: str) -> List[Dict[str, str]]:
        """Identify potential security issues in Cairo code"""
        issues = []
        
        # Check for missing access control
        if not re.search(r'assert!\(.*get_caller_address', content):
            issues.append({
                "severity": "medium",
                "category": "access_control",
                "description": "No caller address validation found",
                "recommendation": "Add assert!(get_caller_address() == expected_address, 'Unauthorized');"
            })
        
        # Check for unchecked external calls
        external_calls = re.findall(r'call_contract_syscall', content)
        if external_calls:
            issues.append({
                "severity": "high",
                "category": "external_calls",
                "description": f"Found {len(external_calls)} external calls - ensure proper validation",
                "recommendation": "Validate return values and implement CEI pattern"
            })
        
        # Check for missing input validation
        functions = re.findall(r'fn\s+\w+\([^)]*\)', content)
        assert_count = len(re.findall(r'assert!\(', content))
        if len(functions) > assert_count:
            issues.append({
                "severity": "medium", 
                "category": "input_validation",
                "description": "Functions may be missing input validation",
                "recommendation": "Add assert! macros to validate function parameters"
            })
        
        # Check for storage write without proper checks
        storage_writes = re.findall(r'\.write\(', content)
        if storage_writes and assert_count < len(storage_writes):
            issues.append({
                "severity": "low",
                "category": "state_management",
                "description": "Storage writes may lack proper validation",
                "recommendation": "Validate conditions before state changes"
            })
        
        return issues
    
    def generate_recommendations(self, content: str) -> List[str]:
        """Generate security recommendations for the contract"""
        recommendations = []
        
        # General recommendations
        recommendations.append("Implement comprehensive access control using owner/role patterns")
        recommendations.append("Use assert! macros for input validation at function entry")
        recommendations.append("Follow Checks-Effects-Interactions pattern for external calls")
        recommendations.append("Add events for important state changes")
        
        # Specific recommendations based on content
        if not re.search(r'#\[event\]', content):
            recommendations.append("Add events for audit trail and monitoring")
        
        if not re.search(r'get_caller_address', content):
            recommendations.append("Implement caller address validation for restricted functions")
        
        if re.search(r'Map<', content):
            recommendations.append("Validate map keys and handle non-existent entries properly")
        
        return recommendations
    
    def calculate_audit_score(self, analysis: Dict[str, Any]) -> int:
        """Calculate audit score based on analysis (0-100)"""
        score = 100
        
        # Deduct points for security issues
        for issue in analysis.get("security_issues", []):
            if issue["severity"] == "high":
                score -= 25
            elif issue["severity"] == "medium":
                score -= 15
            elif issue["severity"] == "low":
                score -= 5
        
        # Bonus points for good structure
        structure = analysis.get("contract_structure", {})
        if structure.get("has_interface"):
            score += 5
        if structure.get("has_constructor"):
            score += 5
        if structure.get("events", 0) > 0:
            score += 5
        
        return max(0, min(100, score))
    
    def audit_project_contracts(self, project_root: str) -> Dict[str, Any]:
        """Audit all Cairo contracts in a project"""
        contracts_path = Path(project_root) / "src" / "contracts"
        
        if not contracts_path.exists():
            return {"error": "No contracts directory found"}
        
        project_audit = {
            "project_root": project_root,
            "contracts_analyzed": 0,
            "total_issues": 0,
            "average_score": 0,
            "contract_reports": [],
            "summary": {}
        }
        
        cairo_files = list(contracts_path.glob("*.cairo"))
        
        for cairo_file in cairo_files:
            contract_analysis = self.analyze_contract_file(str(cairo_file))
            project_audit["contract_reports"].append(contract_analysis)
            project_audit["contracts_analyzed"] += 1
            project_audit["total_issues"] += len(contract_analysis.get("security_issues", []))
        
        # Calculate average score
        if project_audit["contracts_analyzed"] > 0:
            total_score = sum(report.get("audit_score", 0) for report in project_audit["contract_reports"])
            project_audit["average_score"] = total_score / project_audit["contracts_analyzed"]
        
        # Generate summary
        project_audit["summary"] = self.generate_project_summary(project_audit)
        
        return project_audit
    
    def generate_project_summary(self, project_audit: Dict[str, Any]) -> Dict[str, Any]:
        """Generate project-level security summary"""
        issues_by_severity = {"high": 0, "medium": 0, "low": 0}
        issues_by_category = {}
        
        for report in project_audit["contract_reports"]:
            for issue in report.get("security_issues", []):
                severity = issue["severity"]
                category = issue["category"] 
                
                issues_by_severity[severity] += 1
                issues_by_category[category] = issues_by_category.get(category, 0) + 1
        
        return {
            "contracts_count": project_audit["contracts_analyzed"],
            "average_audit_score": round(project_audit["average_score"], 2),
            "issues_by_severity": issues_by_severity,
            "issues_by_category": issues_by_category,
            "recommendations": [
                "Address all high-severity issues before deployment",
                "Implement comprehensive testing for identified vulnerabilities",
                "Consider external security audit for production contracts",
                "Establish ongoing security monitoring and update procedures"
            ]
        }

def main():
    """Main function for CLI usage"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python cairo_audit_assistant.py <project_root>")
        sys.exit(1)
    
    project_root = sys.argv[1]
    assistant = CairoAuditAssistant()
    
    print("=== Cairo Smart Contract Security Audit ===")
    audit_results = assistant.audit_project_contracts(project_root)
    
    if "error" in audit_results:
        print(f"Error: {audit_results['error']}")
        return
    
    # Print summary
    summary = audit_results["summary"]
    print(f"\nProject: {project_root}")
    print(f"Contracts Analyzed: {summary['contracts_count']}")
    print(f"Average Audit Score: {summary['average_audit_score']}/100")
    print(f"Total Issues: {audit_results['total_issues']}")
    
    print("\nIssues by Severity:")
    for severity, count in summary["issues_by_severity"].items():
        print(f"  {severity.upper()}: {count}")
    
    print("\nIssues by Category:")
    for category, count in summary["issues_by_category"].items():
        print(f"  {category.replace('_', ' ').title()}: {count}")
    
    print("\nRecommendations:")
    for rec in summary["recommendations"]:
        print(f"  • {rec}")

if __name__ == "__main__":
    main()