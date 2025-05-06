# Research Assistant

A powerful web application that helps researchers and academics search, analyze, and summarize academic papers efficiently. Built with Python, Flask, and modern web technologies.

![Research Assistant](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.0%2B-green.svg)

## Features

- 🔍 **Smart Paper Search**: Search academic papers across multiple sources including arXiv
- 📚 **Paper Analysis**: Get detailed analysis of papers including key findings, methodology, and conclusions
- 📝 **Paper Summarization**: Generate concise summaries of research papers
- 🎯 **Advanced Filtering**: Filter results by year, citations, and relevance
- 💻 **Modern UI**: Clean, responsive interface built with Bootstrap 5
- 🔄 **Real-time Updates**: Dynamic loading and error handling

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Ollama (for local LLM support)
- Internet connection for paper fetching

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/research-assistant.git
cd research-assistant
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```


## Usage

1. Start the Flask development server:
```bash
python main.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. Enter your search query and configure the number of results you want to see.

4. Click "Search" to fetch relevant papers.

5. Use the "Summarize Paper" button on any paper to get a detailed analysis.

## Project Structure

```
research_assistant/
├── web/
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   ├── templates/
│   └── app.py
├── analysis/
│   └── __init__.py
├── search.py
├── main.py
└── requirements.txt
```

## API Endpoints

- `POST /api/search`: Search for papers
- `POST /api/analyze`: Analyze a specific paper

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [arXiv API](https://arxiv.org/help/api) for paper search functionality
- [Bootstrap](https://getbootstrap.com/) for the UI framework
- [Font Awesome](https://fontawesome.com/) for icons
- [Ollama](https://ollama.ai/) for local LLM support

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.

---
