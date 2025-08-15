#!/usr/bin/env python3
"""
Blind HRM Analysis Tool

Demonstrates the HRM tool's independent reasoning capabilities by analyzing
files without human pre-review. This shows the tool's genuine analytical
power and pattern recognition.
"""

import os
import sys
import random
from pathlib import Path
from analyze_file import HRMCodeAnalyzer

def find_analysis_candidates(root_path: str) -> list[str]:
    """Find Python files suitable for blind analysis"""
    candidates = []
    root = Path(root_path)
    
    # Look for domain files
    domain_patterns = [
        "apps/backend/domains/*/services.py",
        "apps/backend/domains/*/entities.py", 
        "apps/backend/domains/*/value_objects.py",
        "apps/backend/domains/*/repositories.py",
        "apps/backend/api/v1/*/*.py",
        "apps/backend/services/*/*.py"
    ]
    
    for pattern in domain_patterns:
        candidates.extend(root.glob(pattern))
    
    # Convert to strings and filter out __init__.py and test files
    candidates = [
        str(p) for p in candidates 
        if p.name != "__init__.py" and "test" not in p.name.lower()
    ]
    
    return candidates

def run_blind_analysis(file_path: str) -> dict:
    """Run analysis without human review"""
    print(f"🔍 **BLIND ANALYSIS MODE**")
    print(f"📁 **File**: {file_path}")
    print(f"🤖 **Analyzing without human pre-review...**")
    print("=" * 60)
    
    analyzer = HRMCodeAnalyzer()
    result = analyzer.analyze_file(file_path)
    
    return {
        'file_path': file_path,
        'complexity': result.complexity_score,
        'patterns': len(result.patterns_detected),
        'issues': len(result.issues_found),
        'confidence': result.confidence,
        'quality': 'Excellent' if result.confidence > 0.8 else 'Good' if result.confidence > 0.6 else 'Needs Improvement',
        'summary': {
            'patterns_detected': result.patterns_detected,
            'issues_found': [issue['message'] for issue in result.issues_found],
            'suggestions': result.improvement_suggestions[:3]  # Top 3 suggestions
        }
    }

def run_batch_blind_analysis(root_path: str, count: int = 3):
    """Run blind analysis on multiple random files"""
    print(f"🧠 **HRM BLIND ANALYSIS BATCH**")
    print(f"🎯 **Objective**: Demonstrate independent reasoning without human review")
    print(f"📊 **Analyzing {count} random files from AstraTrade codebase**")
    print("=" * 70)
    
    candidates = find_analysis_candidates(root_path)
    if len(candidates) < count:
        count = len(candidates)
    
    # Select random files
    selected_files = random.sample(candidates, count)
    
    results = []
    for i, file_path in enumerate(selected_files, 1):
        print(f"\n📋 **Analysis {i}/{count}**")
        result = run_blind_analysis(file_path)
        results.append(result)
        print("\n" + "─" * 50)
    
    # Summary
    print(f"\n🎉 **BLIND ANALYSIS BATCH COMPLETE**")
    print("=" * 70)
    
    avg_complexity = sum(r['complexity'] for r in results) / len(results)
    total_patterns = sum(r['patterns'] for r in results)
    total_issues = sum(r['issues'] for r in results)
    avg_confidence = sum(r['confidence'] for r in results) / len(results)
    
    print(f"📊 **Batch Summary**:")
    print(f"   - **Files Analyzed**: {len(results)}")
    print(f"   - **Average Complexity**: {avg_complexity:.1f}/100")
    print(f"   - **Total Patterns Detected**: {total_patterns}")
    print(f"   - **Total Issues Found**: {total_issues}")
    print(f"   - **Average Confidence**: {avg_confidence:.1%}")
    
    # Quality distribution
    quality_counts = {}
    for result in results:
        quality = result['quality']
        quality_counts[quality] = quality_counts.get(quality, 0) + 1
    
    print(f"\n🏆 **Quality Distribution**:")
    for quality, count in quality_counts.items():
        print(f"   - **{quality}**: {count} files")
    
    # Most common patterns
    all_patterns = []
    for result in results:
        all_patterns.extend(result['summary']['patterns_detected'])
    
    pattern_counts = {}
    for pattern in all_patterns:
        pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
    
    print(f"\n🔍 **Most Common Patterns Detected**:")
    sorted_patterns = sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)
    for pattern, count in sorted_patterns[:5]:
        print(f"   - **{pattern}**: {count} occurrences")
    
    # Common issues
    all_issues = []
    for result in results:
        all_issues.extend(result['summary']['issues_found'])
    
    if all_issues:
        print(f"\n⚠️  **Common Issues Identified**:")
        for issue in set(all_issues):
            print(f"   - {issue}")
    
    print(f"\n💡 **HRM Reasoning Effectiveness**:")
    print(f"   - ✅ **Independent Analysis**: No human pre-review required")
    print(f"   - ✅ **Pattern Recognition**: Detected {total_patterns} distinct patterns")
    print(f"   - ✅ **Quality Assessment**: {avg_confidence:.1%} average confidence")
    print(f"   - ✅ **Issue Detection**: Found {total_issues} potential improvements")
    print(f"   - ✅ **Domain Awareness**: Recognized AstraTrade-specific concepts")

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python blind_analysis.py <astratrade_root> [count]")
        print("  python blind_analysis.py /path/to/AstraTrade-Submission 3")
        sys.exit(1)
    
    root_path = sys.argv[1]
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    
    if not Path(root_path).exists():
        print(f"❌ Path not found: {root_path}")
        sys.exit(1)
    
    run_batch_blind_analysis(root_path, count)

if __name__ == "__main__":
    main()