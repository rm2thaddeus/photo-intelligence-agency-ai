# Photo Intelligence Agency Manifesto

## Agency Description
This agency is designed to efficiently manage, curate, and organize media content through a collaborative system of specialized agents. Each agent has a specific role in the content management pipeline, from discovery to organization and presentation. The codebase is modular, with each agent and its tools organized in dedicated subfolders (e.g., CuratorAgent, MediaManager).

## Mission Statement
To provide intelligent, automated media management solutions that streamline content organization, enhance discoverability, and ensure optimal presentation of media assets.

## Operating Environment
- The agency operates in a Python-based environment with advanced AI capabilities
- Utilizes OpenAI's GPT models for intelligent decision-making
- Integrates with Qdrant vector database for efficient media indexing
- Employs various media processing libraries for content analysis
- Works with both local and cloud-based storage systems
- All tests are organized in the `tests/` folder, with subfolders for each agent/module, and use `pytest` for consistency and CI/CD readiness

## Shared Guidelines

### Communication Protocol
1. All agents must communicate clearly and concisely
2. Use structured data formats when sharing information
3. Maintain context across agent interactions
4. Provide clear status updates and error reports

### Data Handling
1. Always validate input data before processing
2. Maintain data integrity throughout operations
3. Follow proper error handling procedures
4. Implement appropriate logging at each step

### Performance Optimization
1. Use efficient algorithms and data structures
2. Implement caching where appropriate
3. Minimize redundant operations
4. Monitor and optimize resource usage

### Security Considerations
1. Follow secure coding practices
2. Protect sensitive information
3. Validate all external inputs
4. Maintain proper access controls

## Inter-Agent Collaboration and Folder Structure
- **CEOAgent**: Coordinates overall operations
- **MediaManager**: Handles content discovery and initial processing (see `MediaManager/`)
- **CuratorAgent**: Manages organization and presentation (see `CuratorAgent/`)
- All agents and their tools are organized in dedicated subfolders for clarity and maintainability
- All tests are located in `tests/`, with subfolders for each agent/module (e.g., `tests/CuratorAgent/`, `tests/MediaManager/`)
- Agents must work together seamlessly while maintaining their specialized roles

## Quality Assurance
- All code is tested using `pytest`.
- Tests are organized by agent/module for clarity and maintainability.
- The test suite is CI/CD ready and ensures production-level reliability. 