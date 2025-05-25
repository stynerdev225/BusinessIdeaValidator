"""
Business Idea Validator package.
"""

import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import main functionality
from business_validator.validator import validate_business_idea, print_validation_report

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Create necessary directories
os.makedirs("logs", exist_ok=True)
os.makedirs("validation_data", exist_ok=True)
