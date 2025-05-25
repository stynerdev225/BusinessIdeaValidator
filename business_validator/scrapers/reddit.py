"""
Reddit scraper for business idea validation.
"""
import os
import logging
import requests
from time import sleep
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

def search_reddit(keyword, max_pages=3, max_results=10, api_key=None):
    """
    Search Reddit for posts related to a keyword.
    
    Args:
        keyword: Keyword to search for
        max_pages: Maximum number of pages to search
        max_results: Maximum number of results to return
        api_key: ScraperAPI key for web scraping
        
    Returns:
        List of dictionaries with post data
    """
    logging.info(f"Searching Reddit for: {keyword}")
    
    # Use ScraperAPI if available
    if api_key:
        base_url = f"http://api.scraperapi.com?api_key={api_key}&url="
    else:
        base_url = ""
    
    # Build the search URL
    encoded_keyword = quote_plus(keyword)
    search_url = f"{base_url}https://www.reddit.com/search/?q={encoded_keyword}"
    
    try:
        # Make the request
        response = requests.get(
            search_url, 
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            },
            timeout=30  # Added timeout for the request
        )
        
        if response.status_code != 200:
            logging.error(f"Failed to search Reddit: {response.status_code}")
            return []
        
        # Parse the response
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract post data
        results = []
        post_elements = soup.select('div[data-testid="post-container"]')
        
        for post in post_elements[:max_results]:
            try:
                # Extract title
                title_elem = post.select_one('h3')
                title = title_elem.text if title_elem else "No title"
                
                # Extract subreddit
                subreddit_elem = post.select_one('a[data-testid="subreddit-name"]')
                subreddit = subreddit_elem.text if subreddit_elem else ""
                
                # Extract link to post
                link_elem = post.select_one('a[data-testid="post-title"]')
                link = link_elem['href'] if link_elem and 'href' in link_elem.attrs else ""
                
                # Make sure it's a full URL
                if link and link.startswith('/r/'):
                    link = f"https://www.reddit.com{link}"
                
                # Extract post content
                content = ""
                votes = 0
                
                # Try to get votes
                votes_elem = post.select_one('div[data-testid="post-score"]')
                if votes_elem:
                    votes_text = votes_elem.text.strip()
                    try:
                        # Convert k to thousands (e.g., "1.2k" -> 1200)
                        if 'k' in votes_text.lower():
                            votes = int(float(votes_text.lower().replace('k', '')) * 1000)
                        else:
                            votes = int(votes_text)
                    except ValueError:
                        pass
                
                results.append({
                    "title": title,
                    "subreddit": subreddit,
                    "link": link,
                    "url": link,  # Adding url field for deduplication
                    "votes": votes,
                    "content": content  # We'll fetch the full content in another function
                })
                
                # Be nice to the server
                sleep(1)
                
            except Exception as e:
                logging.warning(f"Error parsing Reddit post: {e}")
        
        logging.info(f"Found {len(results)} Reddit posts for: {keyword}")
        return results
        
    except Exception as e:
        logging.error(f"Error searching Reddit: {e}")
        return []

def get_reddit_comments(post_url, api_key=None, max_comments=20):
    """
    Get comments for a Reddit post.
    
    Args:
        post_url: URL of the Reddit post
        api_key: ScraperAPI key for web scraping
        max_comments: Maximum number of comments to retrieve
        
    Returns:
        Dictionary with post content and comments
    """
    logging.info(f"Getting Reddit comments for: {post_url}")
    
    # Use ScraperAPI if available
    if api_key:
        base_url = f"http://api.scraperapi.com?api_key={api_key}&url="
        full_url = f"{base_url}{post_url}"
    else:
        full_url = post_url
    
    try:
        # Make the request
        response = requests.get(
            full_url, 
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            },
            timeout=30  # Added timeout for the request
        )
        
        if response.status_code != 200:
            logging.error(f"Failed to get Reddit comments: {response.status_code}")
            return {"content": "", "comments": []}
        
        # Parse the response
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get post content
        post_content = ""
        post_elem = soup.select_one('div[data-testid="post-container"]')
        if post_elem:
            post_text = post_elem.select_one('div[data-click-id="text"] div')
            if post_text:
                post_content = post_text.text
        
        # Get comments
        comments = []
        comment_elements = soup.select('div[data-testid="comment"]')
        
        for comment in comment_elements[:max_comments]:
            try:
                # Extract comment author
                author_elem = comment.select_one('a[data-testid="comment_author"]')
                author = author_elem.text if author_elem else "Unknown user"
                
                # Extract comment text
                text_elem = comment.select_one('div[data-testid="comment"] > div:nth-child(2)')
                text = text_elem.text if text_elem else ""
                
                # Extract comment score
                score_elem = comment.select_one('div[id*="vote-arrows"]')
                score = 0
                if score_elem:
                    score_text = score_elem.text.strip()
                    try:
                        if 'k' in score_text.lower():
                            score = int(float(score_text.lower().replace('k', '')) * 1000)
                        else:
                            score = int(score_text)
                    except ValueError:
                        pass
                
                comments.append({
                    "author": author,
                    "text": text,
                    "score": score
                })
                
            except Exception as e:
                logging.warning(f"Error parsing Reddit comment: {e}")
        
        # Combine post content and comments
        combined_text = post_content + "\n\n"
        combined_text += "\n".join([f"Comment by {c['author']} (Score: {c['score']}):\n{c['text']}\n" for c in comments])
        
        return {
            "content": post_content,
            "comments": comments,
            "combined_text": combined_text
        }
        
    except Exception as e:
        logging.error(f"Error getting Reddit post content: {e}")
        return {"content": "", "comments": []}
