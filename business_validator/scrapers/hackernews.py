"""
HackerNews scraper for business idea validation.
"""
import os
import logging
import requests
from time import sleep
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

def search_hackernews(keyword, max_pages=3, max_results=10, api_key=None):
    """
    Search HackerNews for posts related to a keyword.
    
    Args:
        keyword: Keyword to search for
        max_pages: Maximum number of pages to search
        max_results: Maximum number of results to return
        api_key: ScraperAPI key for web scraping
        
    Returns:
        List of dictionaries with post data
    """
    logging.info(f"Searching HackerNews for: {keyword}")
    
    # Use ScraperAPI if available
    if api_key:
        base_url = f"http://api.scraperapi.com?api_key={api_key}&url="
    else:
        base_url = ""
    
    # Build the search URL
    encoded_keyword = quote_plus(keyword)
    search_url = f"{base_url}https://hn.algolia.com/?q={encoded_keyword}"
    
    try:
        # Make the request
        response = requests.get(
            search_url, 
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
        
        if response.status_code != 200:
            logging.error(f"Failed to search HackerNews: {response.status_code}")
            return []
        
        # Parse the response
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract post data
        results = []
        post_elements = soup.select('.Story')
        
        for post in post_elements[:max_results]:
            try:
                # Extract title and link
                title_elem = post.select_one('.Story_title a')
                title = title_elem.text if title_elem else "No title"
                link = title_elem['href'] if title_elem and 'href' in title_elem.attrs else ""
                
                # Extract points and comments
                meta_elem = post.select_one('.Story_meta')
                meta_text = meta_elem.text if meta_elem else ""
                
                # Basic extraction of points and comments
                points = 0
                comments = 0
                
                if "points" in meta_text:
                    points_text = meta_text.split("points")[0].strip().split()[-1]
                    try:
                        points = int(points_text)
                    except ValueError:
                        pass
                
                if "comments" in meta_text:
                    comments_text = meta_text.split("comments")[0].strip().split()[-1]
                    try:
                        comments = int(comments_text)
                    except ValueError:
                        pass
                
                # Get the full post content if there's a link
                content = ""
                if link and link.startswith('http'):
                    try:
                        post_url = f"{base_url}{link}" if api_key else link
                        post_response = requests.get(
                            post_url,
                            headers={
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                            }
                        )
                        
                        if post_response.status_code == 200:
                            post_soup = BeautifulSoup(post_response.text, 'html.parser')
                            
                            # Get post text content (this is a simplified approach)
                            post_text = post_soup.select_one('.comment-content')
                            if post_text:
                                content = post_text.text
                    except Exception as e:
                        logging.warning(f"Error getting post content: {e}")
                
                results.append({
                    "title": title,
                    "link": link,
                    "url": link,  # Adding url field for deduplication
                    "points": points,
                    "comments": comments,
                    "content": content,
                    "meta": meta_text
                })
                
                # Be nice to the server
                sleep(1)
                
            except Exception as e:
                logging.warning(f"Error parsing HackerNews post: {e}")
        
        logging.info(f"Found {len(results)} HackerNews posts for: {keyword}")
        return results
        
    except Exception as e:
        logging.error(f"Error searching HackerNews: {e}")
        return []
