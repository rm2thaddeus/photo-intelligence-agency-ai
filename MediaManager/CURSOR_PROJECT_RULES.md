# MediaManager Project Rules

## Environment Setup

### Virtual Environment
- **ALWAYS** use the `venv313` virtual environment for executing code and running tests
- Python version: Python 3.13 (provided by venv313)
- Activation commands:
  - Windows: `..\venv313\Scripts\activate`
  - Linux/Mac: `source ../venv313/bin/activate`

### Testing Procedures
- Before executing any script, ensure the virtual environment is activated
- All test commands should be prefixed with proper virtual environment activation
- Example test command: 
  ```
  ..\venv313\Scripts\activate; python test_script.py
  ```

### PowerShell Command Execution
- **IMPORTANT**: PowerShell in Windows does not support the `&&` operator for command chaining
- Use semicolons (`;`) instead of `&&` for separating commands in PowerShell
- For complex command sequences, use separate lines or create batch/PS1 files
- Example of correct command chaining in PowerShell:
  ```powershell
  cd path/to/dir; python script.py
  ```
- When writing scripts that need to run on both PowerShell and Bash, provide both versions:
  ```powershell
  # PowerShell
  ..\venv313\Scripts\activate; python script.py
  
  # Bash
  source ../venv313/bin/activate && python script.py
  ```

## Code Standards

### Imports and Dependencies
- All dependencies must be installable in the venv313 environment
- Avoid using features specific to Python 3.9 or lower
- Take advantage of Python 3.10+ features where appropriate

### Error Handling
- Always include comprehensive error handling in utility modules
- Log errors using the logger from `processing_utils`
- Provide detailed error messages that indicate the source of failures

### Resource Management
- Properly release resources (file handles, network connections) when done
- Use context managers (`with` statements) whenever possible

## Module Structure

### Processing Utilities
- Keep core processing utilities in `processing_utils.py`
- Initialize shared resources at module level for reuse
- Provide test functions in each module for verification

### Media Processing
- Separate concerns between image and video processing
- Reuse shared code through the common utilities
- Implement consistent interfaces across different media types

## Database Management

### Qdrant Configuration
- Always configure Qdrant connection through environment variables
- Verify connection before performing operations
- Handle connection failures gracefully

### Embeddings
- Use consistent embedding dimensions across all media types
- Store embeddings efficiently for retrieval
- Include metadata with all stored embeddings

## Testing

### Test Scripts
- Create dedicated test scripts for each module
- Run through the venv313 environment only
- Verify dependencies are properly installed in the environment

## Deployment

### Environment Variables
- Store configuration in `.env` file (not committed to version control)
- Access environment variables through `os.getenv()`
- Provide sensible defaults for non-critical configuration

## Documentation

### Code Documentation
- Include docstrings for all functions and classes
- Document parameters, return values, and exceptions
- Add examples for complex operations

### Project Documentation
- Keep this CURSOR_PROJECT_RULES.md file updated
- Document setup procedures for new developers
- Include troubleshooting guides for common issues 