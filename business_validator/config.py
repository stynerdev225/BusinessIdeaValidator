"""
Configuration settings for the business validator.
"""
import os
from pathlib import Path

# Base directory for the project
BASE_DIR = Path(__file__).parent.parent

# Directory for storing validation data
DATA_DIR = os.path.join(BASE_DIR, "validation_data")

# Directory for logs
LOG_DIR = os.path.join(BASE_DIR, "logs")

# Default number of search results to analyze per platform
DEFAULT_HN_POSTS_TO_ANALYZE = 10
DEFAULT_REDDIT_POSTS_TO_ANALYZE = 10

# Default number of keywords to generate and search for
DEFAULT_KEYWORDS_COUNT = 3

# Default max pages to search per keyword
DEFAULT_MAX_PAGES_PER_KEYWORD = 3
