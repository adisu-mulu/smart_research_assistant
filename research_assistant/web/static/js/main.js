document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('searchForm');
    const loadingIndicator = document.querySelector('.loading');
    const resultsContainer = document.querySelector('.results');
    const errorAlert = document.querySelector('.alert-danger');

    if (searchForm) {
        searchForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Show loading indicator
            loadingIndicator.style.display = 'block';
            resultsContainer.innerHTML = '';
            if (errorAlert) errorAlert.style.display = 'none';

            const formData = new FormData(searchForm);
            const query = formData.get('query');
            const maxResults = formData.get('max_results');

            try {
                const response = await fetch('api/search', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        query: query,
                        max_results: parseInt(maxResults)
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    displayResults(data);
                } else {
                    showError(data.error || 'An error occurred while searching');
                }
            } catch (error) {
                showError('Network error occurred. Please try again.');
            } finally {
                loadingIndicator.style.display = 'none';
            }
        });
    }

    function displayResults(data) {
        const papers = data.results || [];
        if (!papers || papers.length === 0) {
            resultsContainer.innerHTML = '<div class="alert alert-info">No results found.</div>';
            return;
        }

        const papersHTML = papers.map(paper => {
            const abstract = paper.abstract || 'No abstract available';
            const shortAbstract = abstract.substring(0, 500);
            const hasMore = abstract.length > 500;
            
            return `
                <div class="card paper-card mb-3">
                    <div class="card-body">
                        <h5 class="card-title">
                            <a href="${escapeHTML(paper.id)}" class="text-decoration-none text-dark" target="_blank">
                                ${escapeHTML(paper.title)}
                            </a>
                        </h5>
                        <h6 class="card-subtitle mb-2 text-muted">
                            Authors: ${escapeHTML(paper.authors ? paper.authors.join(', ') : 'No authors available')}
                        </h6>
                        <div class="mb-2">
                            <span class="badge bg-secondary">
                                ${paper.year || 'Not available'}
                            </span>
                            <span class="badge bg-info">
                                ${paper.citations || 0} citations
                            </span>
                        </div>
                        <h6 class="abstract-heading">Abstract</h6>
                        <div class="abstract-container">
                            <p class="card-text abstract-short">
                                ${escapeHTML(shortAbstract)}${hasMore ? '...' : ''}
                            </p>
                            ${hasMore ? `
                            <p class="card-text abstract-expanded" style="display: none;">
                                ${escapeHTML(abstract)}
                            </p>
                            <div class="abstract-actions">
                                <button class="read-more-btn btn btn-link text-primary">Read More</button>
                            </div>
                            ` : ''}
                        </div>
                        <div class="mt-3">
                            <button class="btn btn-primary summarize-btn" data-paper-id="${paper.id || ''}">
                                <i class="fas fa-book-reader me-2"></i>Summarize Paper
                            </button>
                        </div>
                        <div class="paper-analysis mt-3" style="display: none;">
                            <div class="analysis-loading text-center">
                                <div class="spinner-border text-primary" role="status">
                                    <span class="visually-hidden">Analyzing paper...</span>
                                </div>
                                <p class="mt-2">Analyzing paper...</p>
                            </div>
                            <div class="analysis-content" style="display: none;">
                                <h6 class="analysis-heading">Paper Analysis</h6>
                                <div class="analysis-sections">
                                    <div class="analysis-section">
                                        <h6>Key Findings</h6>
                                        <p class="key-findings"></p>
                                    </div>
                                    <div class="analysis-section">
                                        <h6>Methodology</h6>
                                        <p class="methodology"></p>
                                    </div>
                                    <div class="analysis-section">
                                        <h6>Conclusions</h6>
                                        <p class="conclusions"></p>
                                    </div>
                                    <div class="analysis-section">
                                        <h6>Limitations</h6>
                                        <p class="limitations"></p>
                                    </div>
                                    <div class="analysis-section">
                                        <h6>Future Work</h6>
                                        <p class="future-work"></p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        resultsContainer.innerHTML = papersHTML;

        // Add event listeners for summarize buttons
        document.querySelectorAll('.summarize-btn').forEach(button => {
            button.addEventListener('click', async function() {
                const paperId = this.getAttribute('data-paper-id');
                if (!paperId) return;

                const paperCard = this.closest('.paper-card');
                const analysisContainer = paperCard.querySelector('.paper-analysis');
                const loadingIndicator = analysisContainer.querySelector('.analysis-loading');
                const analysisContent = analysisContainer.querySelector('.analysis-content');

                // Show analysis container and loading indicator
                analysisContainer.style.display = 'block';
                loadingIndicator.style.display = 'block';
                analysisContent.style.display = 'none';
                this.disabled = true;

                try {
                    // Get paper analysis
                    const response = await fetch('/api/analyze', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ paper_id: paperId })
                    });

                    if (!response.ok) {
                        throw new Error('Failed to analyze paper');
                    }

                    const data = await response.json();
                    
                    // Update analysis content
                    const sections = analysisContainer.querySelectorAll('.analysis-section p');
                    sections[0].textContent = data.analysis.key_findings || 'No key findings available';
                    sections[1].textContent = data.analysis.methodology || 'No methodology information available';
                    sections[2].textContent = data.analysis.conclusions || 'No conclusions available';
                    sections[3].textContent = data.analysis.limitations || 'No limitations information available';
                    sections[4].textContent = data.analysis.future_work || 'No future work suggestions available';

                    // Show analysis content
                    loadingIndicator.style.display = 'none';
                    analysisContent.style.display = 'block';
                } catch (error) {
                    console.error('Error analyzing paper:', error);
                    analysisContainer.innerHTML = `
                        <div class="alert alert-danger mt-3">
                            Failed to analyze paper. Please try again later.
                        </div>
                    `;
                } finally {
                    this.disabled = false;
                }
            });
        });

        // Add event listeners for read more buttons
        document.querySelectorAll('.read-more-btn').forEach(button => {
            button.addEventListener('click', function() {
                const abstractContainer = this.closest('.abstract-container');
                const shortAbstract = abstractContainer.querySelector('.abstract-short');
                const abstractExpanded = abstractContainer.querySelector('.abstract-expanded');
                
                if (abstractExpanded.style.display === 'none') {
                    shortAbstract.style.display = 'none';
                    abstractExpanded.style.display = 'block';
                    this.textContent = 'Show Less';
                } else {
                    shortAbstract.style.display = 'block';
                    abstractExpanded.style.display = 'none';
                    this.textContent = 'Read More';
                }
            });
        });
    }

    function showError(message) {
        if (errorAlert) {
            errorAlert.textContent = message;
            errorAlert.style.display = 'block';
        } else {
            resultsContainer.innerHTML = `
                <div class="alert alert-danger" role="alert">
                    ${escapeHTML(message)}
                </div>
            `;
        }
    }

    function escapeHTML(str) {
        if (!str) return '';
        return str
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
}); 