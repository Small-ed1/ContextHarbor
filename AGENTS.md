# AGENTS.md - Router Phase 1 Development Guide

Essential information for agentic coding agents working in this repository.

## Build, Lint, and Test Commands

### Frontend (React + Parcel)
```bash
# Development server
npm start

# Production build
npm run build

# Run all tests
npm test

# Run single test file
npm test -- ResearchControls.test.js

# Run tests with coverage
npm test -- --coverage
```

### Backend (Python + FastAPI)
```bash
# Install dependencies (Arch Linux: pip install --break-system-packages -r requirements.txt)
pip install -r requirements.txt

# Development server
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000

# Run all tests
python -m pytest tests/ -v

# Run single test file
python -m pytest tests/test_specific.py -v

# Type checking
mypy backend/ --ignore-missing-imports

# Code formatting
black backend/ && isort backend/
```

### Production Deployment
```bash
# Automated setup (requires sudo)
./setup-production.sh

# Manual systemd service management
sudo systemctl start router-phase1
sudo systemctl status router-phase1
sudo journalctl -u router-phase1 -f
```

## Code Style Guidelines

### JavaScript/React (Frontend)

#### Imports
```javascript
// React imports first
import React, { useState, useEffect } from 'react';

// Third-party libraries
import { motion } from 'framer-motion';

// Local imports (relative)
import { cachedFetch } from './apiCache';
import RichTextMessage from './RichTextMessage';
```

#### Component Structure
Use React.memo for performance, proper cleanup in useEffect, and displayName for debugging.

#### Naming Conventions
- **Components**: PascalCase (`MyComponent`)
- **Functions**: camelCase (`handleClick`, `formatDate`)
- **Constants**: UPPER_SNAKE_CASE (`MAX_RETRY_COUNT`)
- **Files**: PascalCase for components, camelCase for utilities
- **CSS Classes**: kebab-case (`my-component`)

#### Error Handling
```javascript
const [error, setError] = useState(null);
const [loading, setLoading] = useState(false);

const handleAsyncOperation = async () => {
  try {
    setLoading(true);
    setError(null);
    const result = await someAsyncCall();
  } catch (err) {
    console.error('Operation failed:', err);
    setError(err.message);
  } finally {
    setLoading(false);
  }
};
```

### Python (Backend)

#### Imports
```python
# Standard library first
from __future__ import annotations
import json
from typing import Any, Optional, List, Dict

# Third-party
import httpx
from fastapi import FastAPI, HTTPException

# Local imports
from .utils import helper_function
```

#### Type Hints & Error Handling
```python
def process_data(data: Dict[str, Any]) -> Optional[List[str]]:
    """Process input data and return results."""
    if not data:
        return None

    results: List[str] = []
    for key, value in data.items():
        if isinstance(value, str):
            results.append(value.upper())
    return results

async def api_endpoint(request: UserRequest):
    try:
        if not request.name:
            raise HTTPException(status_code=400, detail="Name required")
        result = await process_user_request(request)
        return {"status": "success", "data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
```

#### Naming Conventions
- **Classes**: PascalCase (`UserManager`, `APIClient`)
- **Functions/Methods**: snake_case (`process_data`, `get_user_by_id`)
- **Constants**: UPPER_SNAKE_CASE (`DEFAULT_TIMEOUT`)
- **Files**: snake_case (`user_manager.py`)
- **Variables**: snake_case (`user_data`)

### General Guidelines

#### File Organization
```
frontend/src/
├── components/          # Reusable components
├── hooks/              # Custom React hooks
├── utils/              # Utility functions
├── api/                # API client functions
├── styles/             # Global styles/CSS
└── __tests__/          # Test files

backend/
├── routes/             # API route handlers
├── models/             # Pydantic models
├── utils/              # Utility functions
├── services/           # Business logic
└── tests/              # Test files
```

#### Commit Messages
```
feat: add user authentication
fix: resolve memory leak in chat sessions
docs: update API documentation
style: format code with black
refactor: simplify component state management
test: add unit tests for user validation
```

#### Documentation
```python
def complex_function(param1: str, param2: Optional[int] = None) -> Dict[str, Any]:
    """
    Process complex data with multiple parameters.

    Args:
        param1: Required string parameter
        param2: Optional integer parameter

    Returns:
        Dictionary containing processed results
    """
```

#### Security Considerations
- Validate all user inputs
- Implement proper authentication/authorization
- Sanitize HTML content in React components
- Use HTTPS in production
- Log security-relevant events

#### Performance Guidelines
- Use React.memo for expensive components
- Implement proper loading states
- Cache API responses appropriately
- Use lazy loading for route components
- Optimize bundle size with code splitting
- Monitor memory usage in long-running operations

This guide ensures consistency across the codebase and helps agents produce high-quality, maintainable code.