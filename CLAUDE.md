# Claude.md - NYC Transportation Optimizer Development Instructions

## Project Context
You are helping build the NYC Transportation Optimizer MVP as described in `transport_mvp.md`. This is a web application that compares transportation options (rideshare, public transit, bikes, scooters) across all modes for NYC trips.

## Code Development Guidelines

### Explanation Requirements:
For each file you create or modify:
1. **Purpose & Role**: Explain what this specific file does in the overall application architecture
2. **Folder Structure Reasoning**: Why this file belongs in its specific directory and how it fits the project organization
3. **Dependencies & Connections**: How this file connects to other parts of the application
4. **Key Implementation Decisions**: Why you chose specific approaches, libraries, or patterns

### Development Approach
- **Technology Stack**: React frontend, Python backend (Flask/FastAPI), PostgreSQL database
- **API Integrations**: Google Maps Platform, Uber API, Lyft API, Citi Bike API, MTA feeds
- **Focus on MVP Scope**: NYC only, core vehicle types only, web app only
- **External Booking**: Deep links to native apps, no in-app payments

### Learning-Focused Development Process
1. **Architecture First**: Start with overall project structure and explain the reasoning
2. **Core Infrastructure**: Build Google Maps integration and basic routing first
3. **API Layer**: Create abstraction layers for all transportation services
4. **Data Models**: Design clean data structures for transportation options
5. **Frontend Components**: Build reusable components for comparison display
6. **Integration**: Connect all services and handle real-time data

### Specific Requirements
- Always explain the **why** behind technical decisions, not just the **what**
- Show how each component fits into the larger system architecture
- Highlight potential challenges and how your implementation addresses them
- Suggest improvements or alternative approaches when relevant
- Point out MVP limitations and how they might be addressed in future iterations
- After creating a file, you MUST ensure that all my questions are answered before writing any more code
- After each file creation, you MUST output the details in the Explanation Requirements section

### Project Analysis Protocol
Before writing any new code:
1. Analyze the current project structure and existing files
2. Identify what's already implemented vs what's missing
3. Determine the logical next step in the development process
4. Explain how the next step builds on existing work
5. Outline any dependencies that need to be addressed first

### Code Quality Standards
- Write production-ready code with proper error handling
- Include comprehensive comments explaining complex logic
- Use consistent naming conventions and project structure
- Implement proper separation of concerns
- Consider scalability and maintainability from the start

## Learning Objectives
Help me understand:
- Modern full-stack application architecture
- API integration patterns and best practices
- Real-time data handling and caching strategies
- Frontend state management for complex data
- Database design for transportation data
- Error handling and fallback strategies
- Performance optimization techniques