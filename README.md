# Smart Research Assistant

An intelligent agent designed to help researchers and academics with their research tasks. This assistant can help with:

- Searching and analyzing research papers
- Extracting key information and insights
- Organizing and summarizing research findings
- Providing relevant citations and references

## Features

- Semantic search across academic databases
- Automatic paper summarization
- Citation management
- Research topic exploration
- Key findings extraction

## Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ```
4. Run the assistant:
   ```bash
   python main.py
   ```

## Project Structure

- `main.py`: Main entry point
- `research_assistant/`: Core assistant module
  - `search.py`: Search functionality
  - `analyzer.py`: Paper analysis
  - `summarizer.py`: Content summarization
  - `utils.py`: Utility functions

## Usage

```python
from research_assistant import ResearchAssistant

assistant = ResearchAssistant()
results = assistant.search_papers("your research topic")
summary = assistant.analyze_paper("paper_id")
```

## License

MIT License 