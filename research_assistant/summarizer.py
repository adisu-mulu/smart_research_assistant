from typing import Dict, Any
import requests
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

class PaperSummarizer:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.3,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.summary_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a research paper summarizer. Create a clear and concise summary of the given paper."),
            ("user", """
            Please summarize this research paper with the following structure:
            1. Main objective
            2. Key methods
            3. Principal findings
            4. Significance and impact
            
            Paper content:
            {content}
            """)
        ])

    def summarize(self, paper_id: str) -> Dict[str, Any]:
        """
        Generate a comprehensive summary of a research paper.
        
        Args:
            paper_id (str): The ID of the paper to summarize
            
        Returns:
            dict: Summary results
        """
        # Get paper content
        paper_content = self._get_paper_content(paper_id)
        
        if not paper_content:
            return {
                "error": "Could not retrieve paper content",
                "paper_id": paper_id
            }
        
        # Generate summary using LLM
        summary = self._generate_summary(paper_content)
        
        return {
            "paper_id": paper_id,
            "summary": summary
        }

    def _get_paper_content(self, paper_id: str) -> str:
        """
        Retrieve paper content from Semantic Scholar API.
        """
        try:
            url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}"
            params = {
                'fields': 'title,abstract,year,authors,venue,publicationVenue,referenceCount,citationCount,openAccessPdf'
            }
            
            response = requests.get(url, params=params)
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
        except Exception as e:
            print(f"Error retrieving paper content: {str(e)}")
            return ""

    def _generate_summary(self, content: str) -> Dict[str, str]:
        """
        Generate summary using LLM.
        """
        try:
            chain = self.summary_prompt | self.llm
            response = chain.invoke({"content": content})
            
            # Parse the response into structured format
            summary_text = response.content
            
            # Extract sections
            sections = {
                "objective": self._extract_section(summary_text, "Main objective"),
                "methods": self._extract_section(summary_text, "Key methods"),
                "findings": self._extract_section(summary_text, "Principal findings"),
                "significance": self._extract_section(summary_text, "Significance and impact")
            }
            
            return sections
        except Exception as e:
            print(f"Error generating summary: {str(e)}")
            return {
                "error": "Failed to generate summary",
                "details": str(e)
            }

    def _extract_section(self, text: str, section_name: str) -> str:
        """
        Extract a specific section from the summary text.
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