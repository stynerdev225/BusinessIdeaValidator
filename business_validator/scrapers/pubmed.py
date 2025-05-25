"""
PubMed scraper for research and scientific findings.
"""
import requests
import logging
from typing import Dict, List, Any
from bs4 import BeautifulSoup
import time
import xml.etree.ElementTree as ET

class PubMedScraper:
    """Scraper for PubMed research articles and scientific findings."""
    
    def __init__(self):
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.pubmed_url = "https://pubmed.ncbi.nlm.nih.gov"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def search_research_data(self, topic: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search PubMed for research data on a specific health topic.
        
        Args:
            topic: Health topic to search for
            limit: Maximum number of results to return
        
        Returns:
            List of dictionaries containing PubMed research findings
        """
        results = []
        
        try:
            # Use PubMed E-utilities to search
            search_url = f"{self.base_url}/esearch.fcgi"
            search_params = {
                'db': 'pubmed',
                'term': f"{topic}[Title/Abstract] AND (epidemiology OR prevalence OR statistics OR trends)",
                'retmax': limit,
                'sort': 'relevance',
                'retmode': 'xml'
            }
            
            response = self.session.get(search_url, params=search_params, timeout=10)
            response.raise_for_status()
            
            # Parse XML response to get article IDs
            root = ET.fromstring(response.content)
            id_list = root.find('IdList')
            
            if id_list is not None:
                article_ids = [id_elem.text for id_elem in id_list.findall('Id')]
                
                # Get details for each article
                for article_id in article_ids[:limit]:
                    article_data = self._get_article_details(article_id)
                    if article_data:
                        results.append(article_data)
                        
            # If no results from E-utilities, try simple web search
            if not results:
                results = self._fallback_web_search(topic, limit)
                        
        except Exception as e:
            logging.error(f"Error scraping PubMed for {topic}: {str(e)}")
            # Return fallback research data
            results.append({
                'source': 'PubMed',
                'title': f'Research Literature on {topic}',
                'url': f"{self.pubmed_url}/?term={topic.replace(' ', '+')}",
                'content': f"PubMed contains extensive research literature on {topic}, including epidemiological studies, clinical trials, and systematic reviews. Search PubMed for peer-reviewed scientific articles on {topic} prevalence, treatment, and prevention strategies.",
                'type': 'research_summary',
                'pmid': 'N/A'
            })
        
        return results
    
    def _get_article_details(self, pmid: str) -> Dict[str, Any]:
        """Get details for a specific PubMed article."""
        try:
            # Use efetch to get article details
            fetch_url = f"{self.base_url}/efetch.fcgi"
            fetch_params = {
                'db': 'pubmed',
                'id': pmid,
                'retmode': 'xml'
            }
            
            response = self.session.get(fetch_url, params=fetch_params, timeout=10)
            response.raise_for_status()
            
            # Parse XML to extract article information
            root = ET.fromstring(response.content)
            article = root.find('.//Article')
            
            if article is not None:
                title_elem = article.find('.//ArticleTitle')
                abstract_elem = article.find('.//Abstract/AbstractText')
                
                title = title_elem.text if title_elem is not None else f"PubMed Article {pmid}"
                abstract = abstract_elem.text if abstract_elem is not None else "Abstract not available"
                
                # Limit abstract length
                if len(abstract) > 500:
                    abstract = abstract[:500] + "..."
                
                return {
                    'source': 'PubMed',
                    'title': title,
                    'url': f"{self.pubmed_url}/{pmid}/",
                    'content': abstract,
                    'type': 'research_article',
                    'pmid': pmid
                }
                
        except Exception as e:
            logging.error(f"Error getting PubMed article details for PMID {pmid}: {str(e)}")
            
        finally:
            time.sleep(0.5)  # Be respectful to NCBI servers
            
        return None
    
    def _fallback_web_search(self, topic: str, limit: int) -> List[Dict[str, Any]]:
        """Fallback web search for PubMed content."""
        results = []
        
        try:
            # Search PubMed web interface
            search_url = f"{self.pubmed_url}/"
            search_params = {'term': f"{topic} epidemiology"}
            
            response = self.session.get(search_url, params=search_params, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for article snippets
            articles = soup.find_all('article', class_='full-docsum')
            
            for article in articles[:limit]:
                title_elem = article.find('a', class_='docsum-title')
                snippet_elem = article.find('div', class_='full-view-snippet')
                
                if title_elem:
                    title = title_elem.get_text().strip()
                    href = title_elem.get('href', '')
                    
                    if href and not href.startswith('http'):
                        href = self.pubmed_url + href
                    
                    snippet = snippet_elem.get_text().strip() if snippet_elem else "Research article abstract"
                    
                    results.append({
                        'source': 'PubMed',
                        'title': title,
                        'url': href,
                        'content': snippet,
                        'type': 'research_article',
                        'pmid': href.split('/')[-2] if '/' in href else 'N/A'
                    })
                    
        except Exception as e:
            logging.error(f"Error in PubMed fallback search: {str(e)}")
            
        return results

def scrape_pubmed_data(topic: str, limit: int = 3) -> List[Dict[str, Any]]:
    """
    Convenience function to scrape PubMed research data for a health topic.
    
    Args:
        topic: Health topic to search for
        limit: Maximum number of results
    
    Returns:
        List of PubMed research results
    """
    scraper = PubMedScraper()
    return scraper.search_research_data(topic, limit)
