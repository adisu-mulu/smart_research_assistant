from .search import PaperSearch
from .analysis import PaperAnalyzer
from .summarizer import PaperSummarizer

class ResearchAssistant:
    def __init__(self):
        self.search_engine = PaperSearch()
        self.analyzer = PaperAnalyzer()
        self.summarizer = PaperSummarizer()

    def search_papers(self, query: str, max_results: int = 10):
        """
        Search for papers related to the given query using Google Scholar.
        
        Args:
            query (str): The search query
            max_results (int): Maximum number of results to return
            
        Returns:
            list: List of paper metadata and abstracts from Google Scholar
        """
        return self.search_engine.search(query, max_results)

    def analyze_paper(self, paper_id: str):
        """
        Analyze a research paper and extract key information.
        
        Args:
            paper_id (str): The ID of the paper to analyze
            
        Returns:
            dict: Analysis results including key findings, methodology, conclusions, etc.
        """
        return self.analyzer.analyze(paper_id)

    def summarize_paper(self, paper_id: str):
        """
        Generate a comprehensive summary of a research paper.
        
        Args:
            paper_id (str): The ID of the paper to summarize
            
        Returns:
            dict: Summary results including main objective, methods, findings, etc.
        """
        return self.summarizer.summarize(paper_id)

    # Removed explore_topic method 