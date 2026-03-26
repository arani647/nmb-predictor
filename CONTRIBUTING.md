# Contributing to NMB Predictor

Welcome! We are excited to have you contribute to this project. This document provides the full context needed to pick up the development seamlessly.

## Architecture

The project is structured into two main components separated into their respective directories:

### Backend (`/backend`)
A Python application built with FastAPI.
* **API Layer**: Handles HTTP requests, Server-Sent Events (SSE) for real-time updates from the simulator, and prediction endpoints.
* **Core Logic (`/backend/pk`)**: Pharmacokinetic/Pharmacodynamic (PK/PD) models. This calculates reversal recommendations and NMB levels over time.
* **Agents (`/backend/agents`)**: Holds logic for LLM-based clinical decision support (via Anthropic).

To develop on the backend locally without Docker:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e ".[dev]"
```

### Frontend (`/frontend`)
A modern web application built with React, Vite, and TypeScript.
* **Styling**: Tailwind CSS is used for all utility-based styling.
* **State Management**: React context or standard hooks (useState, useEffect). Uses Server-Sent Events (SSE) to subscribe to backend updates.

To develop on the frontend locally without Docker:
```bash
cd frontend
npm install
npm run dev
```

## Adding Features

1. **Create an Issue**: Before diving into a large architectural change, please discuss it in the repository's issues.
2. **Branching Strategy**: Use feature branches. Follow a consistent naming convention like `feature/short-description` or `fix/issue-description`.
3. **Commit Messages**: Write clear, descriptive commit messages.

## Testing

When contributing logic to the backend, ensure your code is covered by tests.
Run tests using:
```bash
make test
```

We look forward to collaborating!
