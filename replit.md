# Overview

This is a Flask-based web application that provides a question-answering interface powered by OpenAI's API. The application presents users with a simple web form where they can submit questions and receive AI-generated responses. The project uses a minimalist architecture with server-side rendering and a gradient-styled UI.

The application includes both a user-facing HTML interface and a JSON API endpoint designed for integration with automation platforms like Make.com.

## Recent Changes (November 19, 2025)
- Configured Flask server to run on host 0.0.0.0 and port 5000 for Replit webview compatibility
- Transformed interface into ChatGPT-style chat application with conversation history
- Implemented real-time message handling with JavaScript (no page reloads)
- Added typing indicator animation while waiting for AI responses
- Created dark theme UI with distinct user/AI message bubbles
- Maintained '/api/chat' JSON API endpoint for Make.com automation integration
- Integrated OpenAI gpt-4o-mini model with secure error handling
- Fixed API key whitespace issue for reliable OpenAI connections
- Added mobile-friendly responsive design optimized for all screen sizes

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture

**Server-Side Rendering with Inline Templates**
- The application uses Flask's `render_template_string` to serve HTML directly from Python strings
- CSS styling is embedded inline within the HTML template
- Modern, responsive design using flexbox and gradient backgrounds
- No separate frontend framework or build process required

**Design Rationale**: This approach keeps the application simple and self-contained, avoiding the complexity of separate template files or frontend build tools. It's ideal for small applications where the UI is straightforward and doesn't require frequent updates.

## Backend Architecture

**Flask Microframework**
- Lightweight Python web framework handling HTTP routing and request/response cycles
- RESTful API endpoint structure (implied from the `/` route and typical Flask patterns)
- Environment-based configuration for sensitive credentials

**API Integration Layer**
- OpenAI Python SDK for accessing GPT models
- API key management through environment variables (`OPENAI_API_KEY`)
- Client instantiation at application startup for reuse across requests

**Design Rationale**: Flask was chosen for its simplicity and minimal boilerplate, making it perfect for this lightweight application. The OpenAI client is initialized once at the module level to avoid repeated instantiation on each request.

## Data Storage

**No Persistent Storage**
- The application appears to be stateless with no database integration
- No conversation history or user data persistence
- Each request is independent

**Design Rationale**: For a simple Q&A interface, persistent storage adds unnecessary complexity. The application can scale horizontally without database synchronization concerns.

## Authentication & Authorization

**No Authentication System**
- No user login or session management
- Open access to the question-answering interface

**Design Rationale**: This is a simple demo/prototype application that doesn't require user accounts. API key protection is handled at the infrastructure level through environment variables.

# External Dependencies

## Third-Party Services

**OpenAI API**
- Primary service for natural language processing and question answering
- Accessed via the official `openai` Python package
- Requires valid API key set in environment variables
- Handles the core AI functionality of the application

## Python Packages

**Flask** (Web Framework)
- Handles HTTP routing, request/response handling, and template rendering
- Provides the WSGI application server interface

**OpenAI** (API Client)
- Official Python SDK for OpenAI's API
- Manages authentication, request formatting, and response parsing

## Environment Configuration

**Required Environment Variables**
- `OPENAI_API_KEY`: Authentication credential for OpenAI API access
- Must be set before application startup

**Deployment Considerations**: The application expects to run in an environment where these variables are properly configured (e.g., Replit Secrets, environment files, or cloud platform configuration).