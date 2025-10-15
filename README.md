# Code Review Assistant

An AI-powered automated code review tool with advanced analytics and visualizations.

## Demo Video

[Watch Demo Video](https://drive.google.com/file/d/1_3FuGQjBy5ANb9ptLtCBXV63BRk32CBC/view?usp=drive_link)

## Overview

This application analyzes source code files using AI to identify errors, warnings, and potential improvements. It provides detailed metrics, visualizations, and historical tracking of code quality.

## Features

### Core Functionality
- Single file code analysis with AI-powered insights
- Batch upload capability for analyzing multiple files simultaneously
- Comprehensive error, warning, and suggestion reporting
- Security vulnerability detection
- Performance optimization recommendations

### Analytics and Reporting
- Statistical dashboard with aggregate metrics
- Quality trend tracking over time
- Side-by-side comparison of code versions
- Export functionality for detailed reports
- Search capability across all reviews

### User Interface
- Modern dark theme interface
- Interactive charts and visualizations using Chart.js
- Responsive design with tab-based navigation
- Real-time analysis feedback

## Technology Stack

### Backend
- Framework: Flask 3.0
- AI Integration: Groq API (LLaMA 3.3 70B model)
- Database: SQLite
- Language: Python 3.7+

### Frontend
- Core: HTML5, CSS3, JavaScript
- Visualizations: Chart.js
- Architecture: Single Page Application

## Supported Languages

The tool can analyze code written in:
Python, JavaScript, TypeScript, Java, C, C++, Go, Rust, PHP, Ruby, Swift, Kotlin, C#, Scala, HTML, CSS

## Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager
- Groq API key (free tier available)

### Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/prxthviraj/code-review-assistant.git
cd code-review-assistant
```

2. Set up the backend:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Configure environment variables:

Create a file named `.env` in the backend directory with the following content:
```
GROQ_API_KEY=your_actual_api_key_here
```

To obtain a free API key:
- Visit https://console.groq.com
- Create an account
- Navigate to API Keys section
- Generate a new key

4. Initialize the database:
```bash
python3 app/database.py
```

5. Start the backend server:
```bash
python3 app/api.py
```

The backend will run on http://localhost:5001

6. In a new terminal, start the frontend server:
```bash
cd frontend
python3 -m http.server 8000
```

The frontend will run on http://localhost:8000

7. Access the application:

Open your web browser and navigate to http://localhost:8000

## Usage Guide

### Single File Analysis
1. Navigate to the Upload tab
2. Click the upload area or drag a code file
3. Click "Analyze Code"
4. Review the detailed analysis including scores, charts, and specific issues

### Batch Analysis
1. Navigate to the Batch Upload tab
2. Select up to 10 code files
3. Click "Analyze All Files"
4. View summary results for all files

### Viewing Statistics
1. Navigate to the Statistics tab
2. Click Refresh to load current metrics
3. View aggregate data across all reviews

### Comparing Code Versions
1. Navigate to the Compare tab
2. Select two reviews from the dropdown menus
3. Click Compare to see differences
4. Review quality score changes and issue counts

### Searching Reviews
1. Navigate to the Search tab
2. Enter a filename in the search box
3. View matching results
4. Click Export to download a specific review

### Tracking Trends
1. Navigate to the Trends tab
2. Select a time period (7, 14, or 30 days)
3. View the quality trend chart

## API Endpoints

The backend provides the following REST API endpoints:

- `GET /` - API health check
- `POST /api/review` - Analyze a single file
- `POST /api/batch-review` - Analyze multiple files
- `GET /api/reviews` - Retrieve all reviews
- `GET /api/review/<id>` - Get specific review details
- `DELETE /api/review/<id>` - Delete a review
- `DELETE /api/reviews` - Delete all reviews
- `GET /api/statistics` - Get aggregate statistics
- `GET /api/reviews/search?q=<query>` - Search reviews
- `POST /api/reviews/compare` - Compare two reviews
- `GET /api/trends?days=<n>` - Get quality trends
- `GET /api/review/<id>/export` - Export review as JSON

## Project Structure
```
code-review-assistant/
├── backend/
│   ├── app/
│   │   ├── api.py              # Flask API routes
│   │   ├── database.py         # Database operations
│   │   └── llm_analyzer.py     # AI integration
│   ├── database/               # SQLite database storage
│   ├── .env                    # Environment variables (not in repo)
│   ├── .env.example           # Environment template
│   └── requirements.txt        # Python dependencies
├── frontend/
│   └── index.html             # Single-page application
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## Security Considerations

- API keys are stored in environment variables, never committed to version control
- File uploads are limited to 16MB
- Input validation on all file uploads
- SQL injection prevention through parameterized queries
- CORS configured for local development

## Development

### Running Tests

Currently, manual testing is performed through the web interface.

### Making Changes

After modifying code:
```bash
git add .
git commit -m "Description of changes"
git push
```

## Author

Prithviraj
GitHub: https://github.com/prxthviraj

## Acknowledgments

- Groq for providing free access to LLaMA 3.3 70B model
- Flask framework for backend infrastructure
- Chart.js for data visualizations

## Support

For issues or questions, please open an issue on the GitHub repository.
