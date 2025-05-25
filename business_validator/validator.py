"""
Main validator functionality.
"""
import json
import logging
import os
import time
from typing import Dict, List, Optional

from business_validator.analyzers.keyword_generator import generate_keywords
from business_validator.analyzers.combined_analyzer import generate_final_analysis
from business_validator.models import CombinedAnalysis
from business_validator.scrapers.hackernews import search_hackernews
from business_validator.scrapers.reddit import search_reddit, get_reddit_comments
from business_validator.utils.environment import setup_environment
from business_validator.utils.reporting import save_json_checkpoint, print_validation_report


def validate_business_idea(
    business_idea: str, 
    keywords_count: int = 3,
    max_pages_per_keyword: int = 3,
    max_hn_posts: int = 10,
    max_reddit_posts: int = 10
) -> Dict:
    """
    Validate a business idea by searching and analyzing online discussions.
    
    Args:
        business_idea: The business idea to validate
        keywords_count: Number of keywords to generate and search for
        max_pages_per_keyword: Max pages to search per keyword
        max_hn_posts: Max HN posts to analyze
        max_reddit_posts: Max Reddit posts to analyze
        
    Returns:
        Dict with validation results
    """
    logging.info(f"Starting validation for business idea: {business_idea}")
    
    # Setup environment (creates unique data directory)
    env = setup_environment(business_idea)
    data_dir = env["data_dir"]
    
    try:
        # Step 1: Generate keywords
        logging.info("Step 1: Generating keywords")
        keywords = generate_keywords(business_idea, num_keywords=keywords_count)
        save_json_checkpoint(
            {"business_idea": business_idea, "keywords": keywords},
            os.path.join(data_dir, "01_keywords.json")
        )
        
        # Step 2: Search HackerNews
        logging.info("Step 2: Searching HackerNews")
        hn_posts = []
        for i, keyword in enumerate(keywords):
            logging.info(f"Searching HN for keyword {i+1}/{len(keywords)}: {keyword}")
            posts = search_hackernews(keyword, max_pages=max_pages_per_keyword)
            save_json_checkpoint(
                posts,
                os.path.join(data_dir, f"02_hn_posts_partial_{i+1}.json")
            )
            hn_posts.extend(posts)
            time.sleep(1)  # Avoid rate limiting
        
        # Deduplicate HN posts by URL
        hn_posts_deduplicated = []
        seen_urls = set()
        for post in hn_posts:
            if post["url"] not in seen_urls:
                seen_urls.add(post["url"])
                hn_posts_deduplicated.append(post)
        
        # Save HN posts
        save_json_checkpoint(
            hn_posts_deduplicated[:max_hn_posts],
            os.path.join(data_dir, "02_hn_posts_complete.json")
        )
        
        # Step 3: Search Reddit
        logging.info("Step 3: Searching Reddit")
        reddit_posts = []
        for i, keyword in enumerate(keywords):
            logging.info(f"Searching Reddit for keyword {i+1}/{len(keywords)}: {keyword}")
            posts = search_reddit(keyword, max_pages=max_pages_per_keyword)
            save_json_checkpoint(
                posts,
                os.path.join(data_dir, f"03_reddit_posts_partial_{i+1}.json")
            )
            reddit_posts.extend(posts)
            time.sleep(1)  # Avoid rate limiting
        
        # Deduplicate Reddit posts by URL
        reddit_posts_deduplicated = []
        seen_urls = set()
        for post in reddit_posts:
            if post["url"] not in seen_urls:
                seen_urls.add(post["url"])
                reddit_posts_deduplicated.append(post)
        
        # Save Reddit posts
        reddit_posts_final = reddit_posts_deduplicated[:max_reddit_posts]
        save_json_checkpoint(
            reddit_posts_final,
            os.path.join(data_dir, "03_reddit_posts_complete.json")
        )
        
        # Step 4: Get Reddit comments for selected posts
        logging.info("Step 4: Getting Reddit comments")
        reddit_posts_with_comments = []
        for i, post in enumerate(reddit_posts_final):
            logging.info(f"Getting comments for Reddit post {i+1}/{len(reddit_posts_final)}")
            comments = get_reddit_comments(post["url"], max_comments=10)
            post_with_comments = {
                "post": post,
                "comments": comments
            }
            reddit_posts_with_comments.append(post_with_comments)
            save_json_checkpoint(
                post_with_comments,
                os.path.join(data_dir, f"04_reddit_comments_partial_{i+1}.json")
            )
            time.sleep(0.5)  # Avoid rate limiting
        
        # Save Reddit posts with comments
        save_json_checkpoint(
            reddit_posts_with_comments,
            os.path.join(data_dir, "04_reddit_comments_complete.json")
        )
        
        # Step 5: Analyze HN posts
        logging.info("Step 5: Analyzing HackerNews posts")
        from business_validator.analyzers.hackernews_analyzer import analyze_hn_post
        hn_posts_to_analyze = hn_posts_deduplicated[:max_hn_posts]
        hn_analyses = []
        
        for i, post in enumerate(hn_posts_to_analyze):
            logging.info(f"Analyzing HN post {i+1}/{len(hn_posts_to_analyze)}")
            analysis = analyze_hn_post(post, business_idea)
            hn_analysis = {
                "post": post,
                "analysis": analysis.dict() if hasattr(analysis, "dict") else analysis
            }
            hn_analyses.append(hn_analysis)
            save_json_checkpoint(
                hn_analysis,
                os.path.join(data_dir, f"05_hn_analyses_partial_{i+1}.json")
            )
        
        # Save HN analyses
        save_json_checkpoint(
            hn_analyses,
            os.path.join(data_dir, "05_hn_analyses_complete.json")
        )
        
        # Step 6: Analyze Reddit posts
        logging.info("Step 6: Analyzing Reddit posts")
        from business_validator.analyzers.reddit_analyzer import analyze_reddit_post
        reddit_analyses = []
        
        for i, post_with_comments in enumerate(reddit_posts_with_comments):
            logging.info(f"Analyzing Reddit post {i+1}/{len(reddit_posts_with_comments)}")
            post = post_with_comments["post"]
            comments = post_with_comments["comments"]
            analysis = analyze_reddit_post(post, comments, business_idea)
            reddit_analysis = {
                "post": post,
                "comments": comments,
                "analysis": analysis.dict() if hasattr(analysis, "dict") else analysis
            }
            reddit_analyses.append(reddit_analysis)
            save_json_checkpoint(
                reddit_analysis,
                os.path.join(data_dir, f"06_reddit_analyses_partial_{i+1}.json")
            )
        
        # Save Reddit analyses
        save_json_checkpoint(
            reddit_analyses,
            os.path.join(data_dir, "06_reddit_analyses_complete.json")
        )
        
        # Step 7: Generate final analysis
        logging.info("Step 7: Generating final analysis")
        final_analysis = generate_final_analysis(
            business_idea=business_idea,
            hn_analyses=hn_analyses,
            reddit_analyses=reddit_analyses,
            keywords=keywords
        )
        
        # Save final analysis
        final_analysis_dict = final_analysis.dict() if hasattr(final_analysis, "dict") else final_analysis
        save_json_checkpoint(
            final_analysis_dict,
            os.path.join(data_dir, "07_final_analysis.json")
        )
        
        # Return results
        return final_analysis_dict
        
    except Exception as e:
        logging.exception(f"Error during validation: {e}")
        raise
