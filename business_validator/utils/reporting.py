"""
Reporting utilities.
"""
import json
import os
from typing import Dict, List, Any


def save_json_checkpoint(data: Any, file_path: str) -> None:
    """
    Save data as a JSON checkpoint file.
    
    Args:
        data: Data to save
        file_path: Path to save the file
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Convert Pydantic models to dict if needed
    if hasattr(data, "dict"):
        data = data.dict()
    
    # Save the data
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_json_checkpoint(file_path: str) -> Any:
    """
    Load data from a JSON checkpoint file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Loaded data
    """
    if not os.path.exists(file_path):
        return None
        
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def print_validation_report(analysis: Dict) -> None:
    """
    Print a formatted validation report to the console.
    
    Args:
        analysis: Analysis data to print
    """
    print("\n" + "="*80)
    print(f"BUSINESS IDEA VALIDATION REPORT")
    print("="*80)
    
    print(f"\nOVERALL SCORE: {analysis['overall_score']}/100")
    
    if analysis['overall_score'] >= 80:
        print("VERDICT: Strongly validated with clear market demand")
    elif analysis['overall_score'] >= 60:
        print("VERDICT: Good validation with some areas to address")
    elif analysis['overall_score'] >= 40:
        print("VERDICT: Mixed validation with significant concerns")
    else:
        print("VERDICT: Poor validation with major issues identified")
    
    print("\nSUMMARY:")
    print(analysis['market_validation_summary'])
    
    print("\nKEY PAIN POINTS DISCOVERED:")
    for point in analysis['key_pain_points']:
        print(f"- {point}")
    
    print("\nEXISTING SOLUTIONS:")
    for solution in analysis['existing_solutions']:
        print(f"- {solution}")
    
    print("\nMARKET OPPORTUNITIES:")
    for opportunity in analysis['market_opportunities']:
        print(f"- {opportunity}")
    
    print("\nRECOMMENDATIONS:")
    for rec in analysis['recommendations']:
        print(f"- {rec}")
    
    print("\nPLATFORM INSIGHTS:")
    for platform in analysis['platform_insights']:
        print(f"\n{platform['platform']}:")
        print(f"  {platform['insights']}")
    
    print("\n" + "="*80 + "\n")
