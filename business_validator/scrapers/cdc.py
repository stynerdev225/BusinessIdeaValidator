"""
CDC (Centers for Disease Control and Prevention) data scraper for U.S. health statistics.
"""
import requests
import logging
from typing import Dict, List, Any
from bs4 import BeautifulSoup
import time

class CDCScraper:
    """Scraper for CDC health data and statistics."""
    
    def __init__(self):
        self.base_url = "https://www.cdc.gov"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def search_health_data(self, topic: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search CDC for health data on a specific topic.
        
        Args:
            topic: Health topic to search for
            limit: Maximum number of results to return
        
        Returns:
            List of dictionaries containing CDC health data
        """
        results = []
        
        try:
            # CDC data and statistics page
            search_urls = [
                f"{self.base_url}/nchs/fastats/default.htm",  # FastStats
                f"{self.base_url}/datastatistics/index.html",  # Data & Statistics
            ]
            
            for search_url in search_urls:
                try:
                    response = self.session.get(search_url, timeout=10)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for links related to the topic
                    links = soup.find_all('a', href=True)
                    
                    for link in links:
                        title = link.get_text().strip()
                        href = link.get('href', '')
                        
                        if topic.lower() in title.lower() and len(title) > 5:
                            if not href.startswith('http'):
                                href = self.base_url + href
                            
                            # Get content from the linked page
                            content = self._get_page_content(href)
                            
                            results.append({
                                'source': 'CDC',
                                'title': title,
                                'url': href,
                                'content': content,
                                'type': 'statistics'
                            })
                            
                            if len(results) >= limit:
                                break
                                
                except Exception as e:
                    logging.error(f"Error accessing CDC URL {search_url}: {str(e)}")
                    continue
                
                if len(results) >= limit:
                    break
                    
            # If no specific data found, create general CDC data
            if not results:
                results.append({
                    'source': 'CDC',
                    'title': f'CDC Health Data on {topic}',
                    'url': f"{self.base_url}/datastatistics/index.html",
                    'content': f"The CDC provides comprehensive U.S. health surveillance data on {topic}, including prevalence, demographics, and trends. The CDC's National Center for Health Statistics (NCHS) collects and analyzes health data for evidence-based public health decisions.",
                    'type': 'general'
                })
                        
        except Exception as e:
            logging.error(f"Error scraping CDC data for {topic}: {str(e)}")
            # Return fallback data
            results.append({
                'source': 'CDC',
                'title': f'CDC Health Information on {topic}',
                'url': 'https://www.cdc.gov',
                'content': f"The CDC tracks and analyzes health data for {topic} in the United States. Visit the CDC website for the latest statistics and health information.",
                'type': 'fallback'
            })
        
        return results
    
    def _get_page_content(self, url: str) -> str:
        """Get content from a CDC page."""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for main content areas
            content_areas = soup.find_all(['div', 'section', 'main'], 
                                        class_=['content', 'main-content', 'body-content', 'module'])
            
            content = ""
            for area in content_areas:
                text = area.get_text().strip()
                if len(text) > 50:  # Only include substantial content
                    content += text + " "
                    
            # Clean up the content
            content = ' '.join(content.split())  # Remove extra whitespace
            
            # Limit content length
            return content[:800] + "..." if len(content) > 800 else content
            
        except Exception as e:
            logging.error(f"Error getting CDC page content from {url}: {str(e)}")
            return "Content unavailable"
        
        finally:
            time.sleep(1)  # Be respectful to CDC servers

def scrape_cdc_data(topic: str, limit: int = 3) -> List[Dict[str, Any]]:
    """
    Convenience function to scrape CDC data for a health topic.
    
    Args:
        topic: Health topic to search for
        limit: Maximum number of results
    
    Returns:
        List of CDC data results
    """
    scraper = CDCScraper()
    return scraper.search_health_data(topic, limit)
