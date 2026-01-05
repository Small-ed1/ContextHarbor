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
Use React.memo for performance, proper cleanup in useEffect, and displayName for debugging.

#### Naming Conventions
- Components: PascalCase (`MyComponent`)
- Functions: camelCase (`handleClick`)
- Constants: UPPER_SNAKE_CASE (`MAX_RETRY_COUNT`)
- CSS Classes: kebab-case (`my-component`)

#### Error Handling
```javascript
const [error, setError] = useState(null);
const [loading, setLoading] = useState(false);

const handleAsync = async () => {
  try {
    setLoading(true);
    setError(null);
    const result = await someAsyncCall();
  } catch (err) {
    console.error('Failed:', err);
    setError(err.message);
  } finally {
    setLoading(false);
  }
};
```

#### Naming Conventions
- Components: PascalCase (`MyComponent`)
- Functions: camelCase (`handleClick`)
- Constants: UPPER_SNAKE_CASE (`MAX_RETRY_COUNT`)
- CSS Classes: kebab-case (`my-component`)

### Python (Backend)

#### Type Hints & Error Handling
```python
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
- Classes: PascalCase (`UserManager`, `APIClient`)
- Functions/Methods: snake_case (`process_data`, `get_user_by_id`)
- Constants: UPPER_SNAKE_CASE (`DEFAULT_TIMEOUT`)
- Files: snake_case (`user_manager.py`)
- Variables: snake_case (`user_data`)

### General Guidelines

#### File Organization
```
frontend/src/
├── components/     # Reusable components
├── utils/         # Utility functions
└── __tests__/     # Test files

backend/
├── routes/        # API route handlers
├── models/        # Pydantic models
└── tests/         # Test files
```

#### Commit Messages
```
feat: add user authentication
fix: resolve memory leak
docs: update API docs
style: format code
refactor: simplify logic
test: add unit tests
```

#### Security & Performance
- Validate all user inputs
- Use HTTPS in production
- Sanitize HTML content
- Use React.memo for expensive components
- Implement proper loading states
- Cache API responses

This guide ensures consistency across the codebase and helps agents produce high-quality, maintainable code.