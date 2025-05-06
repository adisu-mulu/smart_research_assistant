from scholarly import scholarly
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import os
from langchain_community.llms import Ollama
import xml.etree.ElementTree as ET
from datetime import datetime

class PaperSearch:
    def __init__(self):
        self.sources = {
            #'google_scholar': self._search_google_scholar,
           # 'semantic_scholar': self._search_semantic_scholar,  # Removed Semantic Scholar
            'arxiv': self._search_arxiv  # Added arXiv
        }
        
        # Setup requests session with retry logic
        self.session = requests.Session()
        retries = Retry(
            total=10,  # Increased from 5 to 10
            backoff_factor=2,  # Increased from 1 to 2
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]  # Explicitly allow methods
        )
        
        # Setup proxy if available
        proxies = {}
        if os.getenv('HTTP_PROXY'):
            proxies['http'] = os.getenv('HTTP_PROXY')
        if os.getenv('HTTPS_PROXY'):
            proxies['https'] = os.getenv('HTTPS_PROXY')
        
        if proxies:
            self.session.proxies.update(proxies)
        
        # Add longer timeout
        self.session.timeout = (5, 30)  # (connect timeout, read timeout)
        
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        
        # arXiv API endpoint
        self.api_url = "https://export.arxiv.org/api/query"

    def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for papers using arXiv API.
        
        Args:
            query (str): The search query
            max_results (int): Maximum number of results to return
            
        Returns:
            list: List of paper metadata and abstracts
        """
        try:
            results = self._search_arxiv(query, max_results)
            if not results:
                raise Exception("No results found for your query.")
            return results[:max_results]
        except Exception as e:
            print(f"Error during arXiv search: {str(e)}")
            raise e

    def _search_arxiv(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Search arXiv for papers.
        """
        try:
            print(f"Searching arXiv for: {query}")
            
            # Increase max_results to account for potential filtering
            search_max_results = max_results * 2
            
            params = {
                'search_query': f'all:{query}',
                'start': 0,
                'max_results': search_max_results,
                'sortBy': 'relevance',
                'sortOrder': 'descending'
            }
            
            headers = {
                'User-Agent': 'ResearchAssistant/1.0',
                'Accept': 'application/atom+xml'
            }
            
            try:
                response = self.session.get(
                    self.api_url,
                    params=params,
                    headers=headers,
                    timeout=(5, 30)  # (connect timeout, read timeout)
                )
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Initial request failed: {str(e)}")
                # Try one more time with a different User-Agent
                headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                response = self.session.get(
                    self.api_url,
                    params=params,
                    headers=headers,
                    timeout=(5, 30)
                )
                response.raise_for_status()
            
            # Parse XML response
            root = ET.fromstring(response.content)
            
            # Define XML namespaces
            ns = {
                'atom': 'http://www.w3.org/2005/Atom',
                'arxiv': 'http://arxiv.org/schemas/atom'
            }
            
            results = []
            for entry in root.findall('atom:entry', ns):
                try:
                    # Extract authors
                    authors = [author.find('atom:name', ns).text 
                             for author in entry.findall('atom:author', ns)]
                    
                    # Extract publication date
                    published = entry.find('atom:published', ns).text
                    year = datetime.strptime(published, '%Y-%m-%dT%H:%M:%SZ').year
                    
                    # Extract categories (subjects)
                    categories = [cat.get('term') 
                                for cat in entry.findall('arxiv:primary_category', ns)]
                    
                    # Get the arXiv ID from the URL
                    arxiv_id = entry.find('atom:id', ns).text.split('/')[-1].split('v')[0]
                    
                    results.append({
                        'id': f'https://arxiv.org/abs/{arxiv_id}',  # Use the full URL
                        'title': entry.find('atom:title', ns).text.strip(),
                        'authors': authors,
                        'abstract': entry.find('atom:summary', ns).text.strip(),
                        'year': year,
                        'citations': 0,  # arXiv doesn't provide citation counts
                        'venue': categories[0] if categories else 'arXiv',
                        'source': 'arxiv'
                    })
                    print(f"Fetched: {results[-1]['title']}")
                    
                    # Break if we have enough results
                    if len(results) >= max_results:
                        break
                        
                except Exception as e:
                    print(f"Error processing paper: {str(e)}")
                    continue
                
            print(f"Found {len(results)} results from arXiv.")
            return results[:max_results]  # Ensure we return exactly max_results
            
        except requests.exceptions.RequestException as e:
            print(f"Network error during arXiv search: {str(e)}")
            raise Exception("Network error occurred. Please try again.")
        except Exception as e:
            print(f"Error searching arXiv: {str(e)}")
            raise e

    def _search_semantic_scholar(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Search Semantic Scholar for papers.
        """
        try:
            print(f"Searching Semantic Scholar for: {query}")
            
            params = {
                'query': query,
                'limit': max_results,
                'fields': 'paperId,title,abstract,year,authors,venue,url,citationCount,referenceCount'
            }
            
            response = self.session.get(
                self.api_url,
                params=params,
                headers={'User-Agent': 'ResearchAssistant/1.0'}
            )
            response.raise_for_status()
            data = response.json()
            
            results = []
            for paper in data.get('data', []):
                try:
                    results.append({
                        'id': paper.get('url', ''),
                        'title': paper.get('title', ''),
                        'authors': [author.get('name', '') for author in paper.get('authors', [])],
                        'abstract': paper.get('abstract', ''),
                        'year': paper.get('year', ''),
                        'citations': paper.get('citationCount', 0),
                        'venue': paper.get('venue', ''),
                        'source': 'semantic_scholar'
                    })
                    print(f"Fetched: {paper.get('title', 'N/A')}")
                except Exception as e:
                    print(f"Error processing paper: {str(e)}")
                    continue
                
            print(f"Found {len(results)} results from Semantic Scholar.")
            return results
            
        except requests.exceptions.RequestException as e:
            print(f"Network error during Semantic Scholar search: {str(e)}")
            raise Exception("Network error occurred. Please try again.")
        except Exception as e:
            print(f"Error searching Semantic Scholar: {str(e)}")
            raise e

    def _search_google_scholar(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Search Google Scholar for papers.
        """
        # Configure scholarly proxy settings again just in case it was reset
        proxies = {}
        if os.getenv('HTTP_PROXY'):
            proxies['http'] = os.getenv('HTTP_PROXY')
        if os.getenv('HTTPS_PROXY'):
            proxies['https'] = os.getenv('HTTPS_PROXY')
        if proxies:
             scholarly.use_proxy(http_proxy=proxies.get('http'), https_proxy=proxies.get('https'))
        else:
             # Ensure proxy is disabled if not set
             # Check the correct way to disable proxy in scholarly docs if needed
             # For now, we assume calling it without args might work or is unnecessary if never set.
             # scholarly.use_proxy() # Or potentially scholarly.disable_proxy()
             pass # Assuming default is no proxy if not set
             
        try:
            print(f"Searching Google Scholar for: {query}")
            search_query = scholarly.search_pubs(query)
            results = []
            
            for i in range(max_results):
                try:
                    print(f"Fetching result {i+1}...")
                    paper = next(search_query)
                    # Fill the paper details
                    paper = scholarly.fill(paper)
                    results.append({
                        'id': paper.get('pub_url', ''),
                        'title': paper.get('bib', {}).get('title', ''),
                        'authors': paper.get('bib', {}).get('author', []), 
                        'abstract': paper.get('bib', {}).get('abstract', ''),
                        'year': paper.get('bib', {}).get('pub_year', ''),
                        'citations': paper.get('num_citations', 0),
                        'source': 'google_scholar'
                    })
                    print(f"Fetched: {paper.get('bib', {}).get('title', 'N/A')}")
                except StopIteration:
                    print("No more results from Google Scholar.")
                    break
                except Exception as e:
                    print(f"Error fetching a specific paper from Google Scholar: {str(e)}")
                    # Try to continue to the next paper
                    continue # Skip this paper and try the next
                # Increase sleep time to reduce chance of rate limiting
                time.sleep(5) 
                
            print(f"Found {len(results)} results from Google Scholar.")
            return results
        except Exception as e:
            print(f"Error searching Google Scholar: {str(e)}")
            # Reraise the exception to be caught in the main search method
            raise e 

    def _remove_duplicates(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate papers based on title and authors.
        """
        seen = set()
        unique_papers = []
        
        for paper in papers:
            # Create a unique key based on title and first author
            title_key = paper.get('title', '').lower()
            author_key = paper.get('authors', [''])[0].lower() if paper.get('authors') else ''
            key = (title_key, author_key)
            
            if key not in seen or not title_key: # Allow papers with no title through
                seen.add(key)
                unique_papers.append(paper)
                
        return unique_papers 

def test_ollama():
    try:
        print("\nTesting connection to Ollama...")
        llm = Ollama(
            model="llama3.2:latest",
            base_url="http://localhost:11434",
            temperature=0.1
        )
        
        print("Sending test prompt to Ollama...")
        response = llm.invoke("Say 'Hello, I am the local Llama 3.2 model.'")
        print(f"Ollama response: {response}")
        return True
    except Exception as e:
        print(f"Failed to connect to Ollama: {str(e)}")
        return False

if __name__ == "__main__":
    test_ollama()