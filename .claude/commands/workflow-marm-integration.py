#!/usr/bin/env python3
"""
Workflow MARM Integration Module
Provides auto-logging hooks for workflow-comprehensive stages.
"""

import os
import sys
from pathlib import Path

# Add commands directory to path for MARM integration
notebook_commands_dir = os.path.join(os.path.dirname(__file__), 'Notebook')
sys.path.insert(0, notebook_commands_dir)

try:
    from marm_integration import get_marm_integration
    MARM_AVAILABLE = True
except ImportError as e:
    print(f"Warning: MARM integration not available: {e}")
    MARM_AVAILABLE = False

class WorkflowMarmIntegration:
    """Auto-logging integration for workflow-comprehensive stages."""
    
    def __init__(self):
        self.marm = get_marm_integration() if MARM_AVAILABLE else None
        self.auto_logging_enabled = True
    
    def set_auto_logging(self, enabled: bool):
        """Enable or disable auto-logging."""
        self.auto_logging_enabled = enabled
    
    def log_express_stage(self, project_title: str, scope_summary: str = "") -> bool:
        """Auto-log Express stage completion."""
        if not self._can_log():
            return False
        
        summary = f"Express: {project_title} - 4W1H captured"
        details = scope_summary if scope_summary else "Initial scope and assumptions documented"
        
        return self.marm.auto_log_workflow_stage('express', summary, details)
    
    def log_ask_stage(self, assumptions_approved: bool, feedback_summary: str = "") -> bool:
        """Auto-log Ask gate completion."""
        if not self._can_log():
            return False
        
        status = "validated" if assumptions_approved else "needs revision"
        summary = f"Ask Gate: Assumptions {status}"
        details = feedback_summary if feedback_summary else f"Stakeholder review {status}"
        
        return self.marm.auto_log_workflow_stage('ask', summary, details)
    
    def log_explore_stage(self, key_findings: str = "") -> bool:
        """Auto-log Explore stage completion."""
        if not self._can_log():
            return False
        
        summary = "Explore: Context analysis complete"
        details = key_findings if key_findings else "Context, research, requirements, and risks documented"
        
        return self.marm.auto_log_workflow_stage('explore', summary, details)
    
    def log_plan_stage(self, key_decisions: str = "") -> bool:
        """Auto-log Plan stage completion."""
        if not self._can_log():
            return False
        
        summary = "Plan: Architecture designed"
        details = key_decisions if key_decisions else "Implementation plan and test strategy finalized"
        
        return self.marm.auto_log_workflow_stage('plan', summary, details)
    
    def log_code_stage(self, implementation_summary: str = "") -> bool:
        """Auto-log Code stage progress."""
        if not self._can_log():
            return False
        
        summary = "Code: Implementation progress"
        details = implementation_summary if implementation_summary else "Code implementation per plan"
        
        return self.marm.auto_log_workflow_stage('code', summary, details)
    
    def log_test_stage(self, test_results: str = "") -> bool:
        """Auto-log Test stage completion."""
        if not self._can_log():
            return False
        
        summary = "Test: Quality validation complete"
        details = test_results if test_results else "Tests passed, coverage validated"
        
        return self.marm.auto_log_workflow_stage('test', summary, details)
    
    def log_writeup_stage(self, pr_summary: str = "") -> bool:
        """Auto-log Write-up stage completion."""
        if not self._can_log():
            return False
        
        summary = "Write-up: Documentation complete"
        details = pr_summary if pr_summary else "PR description and documentation finalized"
        
        return self.marm.auto_log_workflow_stage('writeup', summary, details)
    
    def log_custom_milestone(self, milestone_name: str, description: str) -> bool:
        """Log custom workflow milestone."""
        if not self._can_log():
            return False
        
        return self.marm.auto_log_workflow_stage('milestone', f"{milestone_name}: {description}")
    
    def _can_log(self) -> bool:
        """Check if auto-logging is possible."""
        return (
            MARM_AVAILABLE and 
            self.marm and 
            self.marm.initialized and 
            self.auto_logging_enabled
        )
    
    def get_workflow_history(self) -> str:
        """Get workflow history from current session."""
        if not self._can_log():
            return "Workflow history not available (MARM not initialized)"
        
        try:
            # Get all notebook entries and filter for workflow stages
            session_info = self.marm.get_session_info()
            if not session_info.get('active_session'):
                return "No active session"
            
            # This would typically parse notebook entries for workflow stages
            # For now, return basic session info
            return f"Active session with {session_info['notebook_count']} entries"
            
        except Exception as e:
            return f"Error retrieving workflow history: {e}"

# Global workflow integration instance
workflow_marm = WorkflowMarmIntegration()

def get_workflow_integration() -> WorkflowMarmIntegration:
    """Get the global workflow MARM integration instance."""
    return workflow_marm

# Convenience functions for direct use in workflow commands
def auto_log_express(project_title: str, scope_summary: str = "") -> bool:
    """Auto-log Express stage - convenience function."""
    return workflow_marm.log_express_stage(project_title, scope_summary)

def auto_log_ask(assumptions_approved: bool, feedback_summary: str = "") -> bool:
    """Auto-log Ask stage - convenience function."""
    return workflow_marm.log_ask_stage(assumptions_approved, feedback_summary)

def auto_log_explore(key_findings: str = "") -> bool:
    """Auto-log Explore stage - convenience function."""
    return workflow_marm.log_explore_stage(key_findings)

def auto_log_plan(key_decisions: str = "") -> bool:
    """Auto-log Plan stage - convenience function."""
    return workflow_marm.log_plan_stage(key_decisions)

def auto_log_code(implementation_summary: str = "") -> bool:
    """Auto-log Code stage - convenience function."""
    return workflow_marm.log_code_stage(implementation_summary)

def auto_log_test(test_results: str = "") -> bool:
    """Auto-log Test stage - convenience function."""
    return workflow_marm.log_test_stage(test_results)

def auto_log_writeup(pr_summary: str = "") -> bool:
    """Auto-log Write-up stage - convenience function."""
    return workflow_marm.log_writeup_stage(pr_summary)

if __name__ == "__main__":
    # Test workflow integration
    print("Testing Workflow MARM Integration...")
    
    if workflow_marm._can_log():
        print("✓ Workflow auto-logging available")
        
        # Test each stage logging function
        test_stages = [
            ("Express", lambda: auto_log_express("Test Project", "Testing integration")),
            ("Ask", lambda: auto_log_ask(True, "Assumptions validated")),
            ("Explore", lambda: auto_log_explore("Key findings documented")),
            ("Plan", lambda: auto_log_plan("Architecture decisions made")),
            ("Code", lambda: auto_log_code("Core features implemented")),
            ("Test", lambda: auto_log_test("All tests passing")),
            ("Write-up", lambda: auto_log_writeup("Documentation complete"))
        ]
        
        for stage_name, log_func in test_stages:
            try:
                success = log_func()
                status = "✓" if success else "✗"
                print(f"{status} {stage_name} stage logging test")
            except Exception as e:
                print(f"✗ {stage_name} stage logging failed: {e}")
    else:
        print("✗ Workflow auto-logging not available")
        if not MARM_AVAILABLE:
            print("  - MARM integration not available")
        elif not workflow_marm.marm:
            print("  - MARM instance not created")
        elif not workflow_marm.marm.initialized:
            print("  - MARM not initialized")
        elif not workflow_marm.auto_logging_enabled:
            print("  - Auto-logging disabled")
    
    print("Workflow integration test complete.")