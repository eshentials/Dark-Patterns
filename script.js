document.addEventListener('DOMContentLoaded', () => {
    const textInput = document.getElementById('textInput');
    const urlInput = document.getElementById('urlInput');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const resultsDiv = document.getElementById('results');
    const loadingDiv = document.getElementById('loading');
    
    // Toggle between URL and text input
    urlInput.addEventListener('input', () => {
        if (urlInput.value.trim()) {
            textInput.disabled = true;
            textInput.placeholder = 'Disabled when URL is provided';
        } else {
            textInput.disabled = false;
            textInput.placeholder = 'Or paste your text here...';
        }
    });
    
    textInput.addEventListener('input', () => {
        if (textInput.value.trim()) {
            urlInput.disabled = true;
            urlInput.placeholder = 'Disabled when text is provided';
        } else {
            urlInput.disabled = false;
            urlInput.placeholder = 'https://example.com';
        }
    });

    // Example patterns for client-side detection
    const urgencyPatterns = [
        // Quantity-based urgency
        { 
            pattern: /\b(only|just)\s+\d+\s+(left|remaining|in stock|available|copy|copies)\b/gi,
            description: "Creates false scarcity by suggesting limited quantity"
        },
        {
            pattern: /\b(only|just)\s+(a few|a couple of|a handful of)\s+(left|remaining|in stock|available)\b/gi,
            description: "Uses vague quantity terms to create urgency"
        },
        // Time-based urgency
        {
            pattern: /\b(ends?|expires?)\s+(in|at|today|tonight|soon|in \d+ (hours?|minutes?|days?))\b/gi,
            description: "Implies time pressure to force quick decisions"
        },
        {
            pattern: /\b(limited\s+time|time\s+limited|flash\s+sale|flash\s+deal)\b/gi,
            description: "Suggests the offer is only available for a short time"
        },
        // Scarcity indicators
        {
            pattern: /\b(almost\s+gone|almost\s+sold\s+out|going\s+fast|selling\s+fast)\b/gi,
            description: "Creates fear of missing out (FOMO)"
        },
        // Social proof urgency
        {
            pattern: /\b(\d+\s+people\s+(are\s+)?(viewing|watching|purchasing|buying|in\s+line))\b/gi,
            description: "Uses social pressure to encourage immediate action"
        },
        // Action-oriented urgency
        {
            pattern: /\b(hurry|act\s+now|don'?t\s+miss|last\s+chance|order\s+now|buy\s+now|shop\s+now)\b/gi,
            description: "Direct commands that pressure immediate action"
        }
    ];

    analyzeBtn.addEventListener('click', async () => {
        const text = textInput.value.trim();
        const url = urlInput.value.trim();
        
        if (!text && !url) {
            showError('Please enter a URL or paste some text to analyze');
            return;
        }
        
        // Validate URL format if provided
        if (url && !isValidUrl(url)) {
            showError('Please enter a valid URL (e.g., https://example.com)');
            return;
        }

        // Show loading state
        loadingDiv.classList.remove('hidden');
        resultsDiv.innerHTML = '';
        analyzeBtn.disabled = true;
        
        try {
            // Prepare data for the server
            const data = {};
            let loadingMessage = 'Analyzing content...';
            
            if (url) {
                data.url = url;
                loadingMessage = 'Crawling and analyzing website. This may take a moment...';
            } else {
                data.text = text;
                // Do client-side pattern detection for text input
                const clientResults = detectPatterns(text);
                if (clientResults.length > 0) {
                    displayResults({ results: clientResults }, text);
                }
            }
            
            // Update loading message
            document.querySelector('#loading p').textContent = loadingMessage;
            
            // Send to server for analysis
            const response = await analyzeWithServer(data);
            
            // If we have a report ID, fetch the full report
            if (response.report_id) {
                const reportResponse = await fetch(`/report/${response.report_id}`);
                if (!reportResponse.ok) {
                    throw new Error('Failed to fetch analysis report');
                }
                const reportData = await reportResponse.json();
                displayResults(reportData, reportData.content_preview || url || text);
            } else {
                displayResults(response, url || text);
            }
            
        } catch (error) {
            console.error('Analysis failed:', error);
            showError(`Analysis failed: ${error.message || 'Unknown error'}`);
        } finally {
            loadingDiv.classList.add('hidden');
            analyzeBtn.disabled = false;
        }
    });

    function detectPatterns(text) {
        const results = [];
        
        urgencyPatterns.forEach(({pattern, description}) => {
            const matches = [...text.matchAll(pattern)];
            if (matches.length > 0) {
                results.push({
                    type: 'False Urgency',
                    description: description,
                    matches: [...new Set(matches.map(match => match[0]))],
                    source: 'client'
                });
            }
        });

        return results;
    }

    async function analyzeWithServer(data) {
        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `Server error: ${response.status} ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error analyzing with server:', error);
            throw error;
        }
    }

    function displayResults(results, originalText) {
        loadingDiv.classList.add('hidden');
        analyzeBtn.disabled = false;
        
        // Reset loading text for next time
        document.querySelector('#loading p').textContent = 'Analyzing content...';
        
        // Clear previous results
        resultsDiv.innerHTML = '';
        
        // Handle error case
        if (results.error) {
            showError(results.error);
            return;
        }
        
        // Show report header if available
        if (results.timestamp || results.url) {
            const header = document.createElement('div');
            header.className = 'result-item report-header';
            header.innerHTML = `
                <h2>Analysis Report</h2>
                ${results.url ? `<p class="report-url">URL: <a href="${results.url}" target="_blank" rel="noopener noreferrer">${results.url}</a></p>` : ''}
                ${results.timestamp ? `<p class="report-timestamp">Analyzed on: ${new Date(results.timestamp).toLocaleString()}</p>` : ''}
            `;
            resultsDiv.appendChild(header);
        }
        
        // Show content preview if available
        if (originalText) {
            const contentSection = document.createElement('div');
            contentSection.className = 'result-item content-preview-section';
            contentSection.innerHTML = `
                <h3>Content Preview</h3>
                <div class="content-preview">
                    <p>${originalText.length > 500 ? originalText.substring(0, 500) + '...' : originalText}</p>
                    ${originalText.length > 500 ? 
                        `<button class="show-more" onclick="this.previousElementSibling.innerHTML = '${originalText.replace(/'/g, "\\'").replace(/\n/g, '\\n')}'; this.remove();">Show Full Content</button>` : ''
                    }
                </div>
            `;
            resultsDiv.appendChild(contentSection);
        }
        
        // Check if results is an object with an analysis field or just the results array
        const resultsArray = results.analysis || (Array.isArray(results) ? results : (results.results || []));
        
        if (!resultsArray || resultsArray.length === 0) {
            const noResults = document.createElement('div');
            noResults.className = 'result-item no-results';
            noResults.innerHTML = `
                <h3>No dark patterns detected</h3>
                <p>The content appears to be free of common dark patterns.</p>
            `;
            resultsDiv.appendChild(noResults);
            return;
        }
        
        // Show analysis results
        resultsArray.forEach((result, index) => {
            const resultElement = document.createElement('div');
            const resultType = (result.type || '').toLowerCase().replace(/\s+/g, '-');
            resultElement.className = `result-item ${resultType} ${result.severity ? `severity-${result.severity.toLowerCase()}` : ''}`;
            
            // Format the matches for display
            let matchesHtml = '';
            if (result.matches && result.matches.length > 0) {
                matchesHtml = `
                    <div class="matches">
                        <strong>Matched patterns:</strong>
                        <ul>
                            ${result.matches.map(match => 
                                `<li>${escapeHtml(match)}</li>`
                            ).join('')}
                        </ul>
                    </div>
                `;
            }
            
            // Handle different result formats
            const description = result.description || result.summary || 'A potential dark pattern was detected.';
            const severity = result.severity ? `
                <div class="severity-badge ${result.severity.toLowerCase()}">
                    ${result.severity}
                </div>` : '';
            
            resultElement.innerHTML = `
                <div class="result-header">
                    <h3>${result.type || 'Pattern Detected'}</h3>
                    ${severity}
                </div>
                <div class="result-content">
                    <p>${description}</p>
                    ${matchesHtml}
                    ${result.explanation ? `<div class="explanation"><strong>Explanation:</strong> ${result.explanation}</div>` : ''}
                    ${result.recommendation ? `<div class="recommendation"><strong>Recommendation:</strong> ${result.recommendation}</div>` : ''}
                </div>
            `;
            
            resultsDiv.appendChild(resultElement);
        });
    }

    function highlightMatches(text, matches) {
        let highlighted = text;
        const uniqueMatches = [...new Set(matches)];
        
        uniqueMatches.forEach(match => {
            const regex = new RegExp(escapeRegExp(match), 'gi');
            highlighted = highlighted.replace(regex, 
                `<span class="highlight">${match}</span>`);
        });
        
        return highlighted.replace(/\n/g, '<br>');
    }

    function escapeRegExp(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    function escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'pattern-card error';
        errorDiv.textContent = message;
        resultsDiv.innerHTML = '';
        resultsDiv.appendChild(errorDiv);
    }
});
