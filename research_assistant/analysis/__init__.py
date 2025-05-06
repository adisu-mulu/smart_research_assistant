from typing import Dict, Any, List
import requests
from langchain_community.llms import Ollama
from langchain.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time

load_dotenv()

class PaperAnalyzer:
    def __init__(self):
        # Initialize Ollama with Llama 3.2
        self.llm = Ollama(
            model="llama3.2:latest",
            base_url="http://localhost:11434",
            temperature=0.1
        )
        
        # Setup requests session with retry logic
        self.session = requests.Session()
        retries = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        
        # Setup proxy if available
        proxies = {}
        if os.getenv('HTTP_PROXY'):
            proxies['http'] = os.getenv('HTTP_PROXY')
        if os.getenv('HTTPS_PROXY'):
            proxies['https'] = os.getenv('HTTPS_PROXY')
        
        if proxies:
            self.session.proxies.update(proxies)
        
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        
        self.analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a research paper analyzer. Analyze the given paper content and extract key information."),
            ("user", """
            Please analyze this research paper and provide:
            1. Key findings and contributions
            2. Methodology used
            3. Main conclusions
            4. Limitations
            5. Future work suggestions
            
            Paper content:
            {content}
            """)
        ])

    def analyze(self, paper_id: str) -> Dict[str, Any]:
        """
        Analyze a research paper and extract key information.
        
        Args:
            paper_id (str): The ID of the paper to analyze
            
        Returns:
            dict: Analysis results
        """
        try:
            # Get paper content
            paper_content = self._get_paper_content(paper_id)
            
            if not paper_content:
                return {
                    "error": "Could not retrieve paper content. Please check if the paper ID is valid and try again.",
                    "paper_id": paper_id
                }
            
            # Analyze using LLM
            analysis = self._analyze_with_llm(paper_content)
            
            if "error" in analysis:
                return {
                    "error": f"Analysis failed: {analysis['error']}",
                    "paper_id": paper_id,
                    "details": analysis.get("details", "")
                }
            
            return {
                "paper_id": paper_id,
                "analysis": analysis
            }
        except Exception as e:
            print(f"Error in analyze method: {str(e)}")
            return {
                "error": "An unexpected error occurred during analysis",
                "paper_id": paper_id,
                "details": str(e)
            }

    def _get_paper_content(self, paper_id: str) -> str:
        """
        Retrieve paper content from Semantic Scholar API.
        """
        # Extract arXiv ID if it's a full URL
        if 'arxiv.org' in paper_id:
            # Extract the ID from URLs like http://arxiv.org/abs/1809.04797v1
            paper_id = paper_id.split('/')[-1].split('v')[0]
        
        for attempt in range(3):
            try:
                url = f"https://api.semanticscholar.org/graph/v1/paper/arXiv:{paper_id}"
                params = {
                    'fields': 'title,abstract,year,authors,venue,publicationVenue,referenceCount,citationCount,openAccessPdf'
                }
                
                response = self.session.get(
                    url, 
                    params=params, 
                    timeout=30,
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
                )
                response.raise_for_status()
                data = response.json()
                
                # Construct paper content
                content = f"""
                Title: {data.get('title', '')}
                Authors: {', '.join([author.get('name', '') for author in data.get('authors', [])])}
                Year: {data.get('year', '')}
                Venue: {data.get('venue', '') or data.get('publicationVenue', {}).get('name', '')}
                Abstract: {data.get('abstract', '')}
                Citations: {data.get('citationCount', 0)}
                References: {data.get('referenceCount', 0)}
                """
                
                return content
            except requests.exceptions.RequestException as e:
                print(f"Attempt {attempt + 1} failed to retrieve paper content: {str(e)}")
                if attempt < 2:  # Don't sleep on the last attempt
                    time.sleep(2 ** attempt)  # Exponential backoff
            except Exception as e:
                print(f"Unexpected error retrieving paper content: {str(e)}")
                if attempt < 2:
                    time.sleep(2 ** attempt)
        
        return ""

    def _analyze_with_llm(self, content: str) -> Dict[str, Any]:
        """
        Analyze paper content using LLM.
        """
        try:
            print("Starting LLM analysis...")
            chain = self.analysis_prompt | self.llm
            response = chain.invoke({"content": content})
            
            if not response or not response.content:
                return {
                    "error": "LLM returned empty response",
                    "details": "The language model did not generate any analysis"
                }
            
            # Parse the response into structured format
            analysis_text = response.content
            print("LLM analysis completed successfully")
            
            # Extract sections using simple parsing
            sections = {
                "key_findings": self._extract_section(analysis_text, "Key findings"),
                "methodology": self._extract_section(analysis_text, "Methodology"),
                "conclusions": self._extract_section(analysis_text, "Main conclusions"),
                "limitations": self._extract_section(analysis_text, "Limitations"),
                "future_work": self._extract_section(analysis_text, "Future work")
            }
            
            # Validate that we got at least some content
            if not any(sections.values()):
                return {
                    "error": "Failed to extract analysis sections",
                    "details": "The language model response could not be parsed into sections"
                }
            
            return sections
        except Exception as e:
            print(f"Error in _analyze_with_llm: {str(e)}")
            return {
                "error": "Failed to analyze paper content with language model",
                "details": str(e)
            }

    def _extract_section(self, text: str, section_name: str) -> str:
        """
        Extract a specific section from the analysis text.
        """
        try:
            start = text.lower().find(section_name.lower())
            if start == -1:
                return ""
            
            # Find the next section or end of text
            next_section = text.lower().find("\n", start)
            if next_section == -1:
                next_section = len(text)
            
            return text[start:next_section].strip()
        except:
            return "" 