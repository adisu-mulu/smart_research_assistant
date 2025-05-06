from research_assistant import ResearchAssistant

def main():
    # Initialize the research assistant
    assistant = ResearchAssistant()
    
    # Example: Search for papers about a specific topic
    topic = "machine learning in healthcare"
    print(f"\nSearching for papers about: {topic}")
    papers = assistant.search_papers(topic, max_results=5)
    
    # Display search results
    print("\nSearch Results:")
    if papers:
        for i, paper in enumerate(papers, 1):
            print(f"\n{i}. {paper.get('title', 'No title available')}")
            # Ensure authors is a list of strings before joining
            authors = paper.get('authors', [])
            if isinstance(authors, list):
                authors_str = ', '.join(map(str, authors))
            else:
                authors_str = str(authors) # Handle unexpected author format
            print(f"   Authors: {authors_str if authors_str else 'No authors available'}")
            print(f"   Year: {paper.get('year', 'Year not available')}")
            print(f"   Citations: {paper.get('citations', 0)}")
            if paper.get('abstract'):
                # Limit abstract length
                abstract = paper['abstract']
                print(f"   Abstract: {abstract[:500]}{'...' if len(abstract) > 500 else ''}")
            else:
                print("   Abstract: Not available")
            print(f"   Source URL: {paper.get('id', 'Not available')}") # ID is now pub_url
    else:
        print("No papers found for this topic.")
    
    # Removed paper analysis section
    
    # Removed topic exploration section

if __name__ == "__main__":
    main() 