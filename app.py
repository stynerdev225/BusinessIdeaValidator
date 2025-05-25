"""
Sample script to demonstrate the business idea validator.
"""
import sys
import logging
from business_validator import validate_business_idea, print_validation_report

def main():
    """Run the business idea validator."""
    # Check if a business idea was provided
    if len(sys.argv) < 2:
        print("Usage: python app.py 'Your business idea here'")
        sys.exit(1)
    
    # Get the business idea from command line argument
    business_idea = sys.argv[1]
    
    print(f"Validating business idea: {business_idea}")
    print("This may take a few minutes...\n")
    
    # Run the validation
    try:
        results = validate_business_idea(
            business_idea=business_idea,
            keywords_count=2,  # Reduce for faster demo
            max_pages_per_keyword=2,  # Reduce for faster demo
            max_hn_posts=5,  # Reduce for faster demo
            max_reddit_posts=5  # Reduce for faster demo
        )
        
        # Print the results
        print_validation_report(results)
        
    except Exception as e:
        logging.exception(f"Error validating business idea: {e}")
        print(f"\nError: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
