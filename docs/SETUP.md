# 🚀 Photo Intelligence Agency Setup Guide

## Prerequisites

- Python 3.9+
- pip
- Git
- Virtual environment tool (venv recommended)
- Qdrant instance (local or cloud)

## Installation Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/rm2thaddeus/photo-intelligence-agency-ai.git
   cd photo-intelligence-agency-ai
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   .\venv\Scripts\activate  # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Set up Qdrant:
   - Local installation instructions
   - Cloud setup guide
   - Collection creation steps

6. Initialize the system:
   ```bash
   python setup.py
   ```

## Configuration

### Environment Variables

Detailed explanation of each environment variable in `.env`:

- OpenAI configuration
- Qdrant settings
- Processing parameters
- Gallery options

### Customization

- Template customization
- Processing pipeline adjustments
- Gallery style modifications

## Verification

Run the test suite to verify the installation:
```bash
pytest
```

## Troubleshooting

Common issues and their solutions:
- Database connection issues
- Environment setup problems
- Dependency conflicts

## Next Steps

- Review the User Guide
- Check the API Documentation
- Explore example usage