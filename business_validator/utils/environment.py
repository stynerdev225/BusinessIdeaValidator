"""
Environment setup utilities.
"""
import os
import json
import logging
from datetime import datetime
from pathlib import Path
import shutil

from business_validator.config import DATA_DIR


def setup_environment(business_idea: str) -> dict:
    """
    Set up the environment for a validation run.
    
    Args:
        business_idea: The business idea being validated
        
    Returns:
        Dictionary with environment information
    """
    # Create a unique run ID based on timestamp and sanitized business idea
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    sanitized_idea = "".join(c for c in business_idea[:30] if c.isalnum() or c.isspace()).strip().replace(" ", "_")
    run_id = f"validation_{sanitized_idea}_{timestamp}"
    
    # Create data directory for this run
    run_data_dir = os.path.join(DATA_DIR, run_id)
    os.makedirs(run_data_dir, exist_ok=True)
    
    # Save basic info
    with open(os.path.join(run_data_dir, "info.json"), "w") as f:
        json.dump({
            "business_idea": business_idea,
            "timestamp": timestamp,
            "run_id": run_id
        }, f)
    
    logging.info(f"Set up environment for validation run: {run_id}")
    
    return {
        "run_id": run_id,
        "data_dir": run_data_dir,
        "timestamp": timestamp
    }


def cleanup_environment(run_id: str = None, keep_last_n: int = 5) -> None:
    """
    Clean up old validation runs, keeping only the most recent ones.
    
    Args:
        run_id: Specific run ID to clean up (if None, will clean up old runs)
        keep_last_n: Number of most recent runs to keep
    """
    if run_id:
        # Clean up specific run
        run_data_dir = os.path.join(DATA_DIR, run_id)
        if os.path.exists(run_data_dir):
            shutil.rmtree(run_data_dir)
            logging.info(f"Cleaned up validation run: {run_id}")
        return
    
    # Clean up old runs
    if not os.path.exists(DATA_DIR):
        return
    
    # Get all run directories sorted by modification time (newest first)
    run_dirs = [os.path.join(DATA_DIR, d) for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d))]
    run_dirs.sort(key=os.path.getmtime, reverse=True)
    
    # Keep the most recent N runs
    for old_dir in run_dirs[keep_last_n:]:
        try:
            shutil.rmtree(old_dir)
            logging.info(f"Cleaned up old validation run: {os.path.basename(old_dir)}")
        except Exception as e:
            logging.error(f"Error cleaning up run {os.path.basename(old_dir)}: {str(e)}")
