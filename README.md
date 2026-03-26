# NMB Predictor

Medical-grade neuromuscular blockade (NMB) predictor clinical dashboard application.

## Overview

This project consists of:
* **Backend**: FastAPI, Anthropic API (for clinical decision support agent), NumPy/SciPy (for simulations)
* **Frontend**: React (Vite), TypeScript, Tailwind CSS
* **Infrastructure**: Docker & Docker Compose

## Prerequisites

* Docker and Docker Compose
* Make (optional, but convenient)

## Getting Started

1. **Environment Variables**
   Copy the example environment file and configure your API keys:
   ```bash
   cp .env.example .env
   ```
   Add your `ANTHROPIC_API_KEY` to the `.env` file for the LLM agent functionality.

2. **Run with Docker (Recommended)**
   You can start the entire stack using the provided Makefile or Docker Compose directly:
   
   Using Make:
   ```bash
   make dev
   ```
   
   Using Docker Compose directly:
   ```bash
   docker-compose up -d --build
   ```

3. **Access the Application**
   * Frontend Application: [http://localhost:5173](http://localhost:5173)
   * Backend API: [http://localhost:8000](http://localhost:8000)
   * API Documentation (Swagger): [http://localhost:8000/docs](http://localhost:8000/docs)

## Available Commands

If using `make`, the following commands are available:
* `make dev`: Start the application in detached mode.
* `make down`: Stop and remove containers.
* `make logs`: Tail logs for all services.
* `make test`: Run backend pytest suite.
* `make shell`: Open a bash shell inside the backend container.
