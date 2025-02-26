# Job Recruitment API Documentation

## Overview

This FastAPI-based job recruitment API is designed to match job postings with potential candidates based on multiple criteria, leveraging Elasticsearch for efficient searching.

## Features

- Retrieve job or candidate details by ID
- Search for matching jobs or candidates with relevance scoring
- Open API (no authentication required)
- Supports filtering by salary, skills, and seniority
- Dockerized for easy deployment
- Includes unit tests for API validation

## Installation

### Prerequisites

- Docker & Docker Compose
- Python 3.8+
- Elasticsearch (Docker setup provided)

### Running Locally

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd job-recruitment-api
   ```
2. Start services using Docker Compose:
   ```bash
   docker-compose up --build
   ```
3. Access the API at `http://localhost:8000`

## API Endpoints

### 1. Retrieve Document by ID

**Endpoint:** `/get-entity`

- **Method:** `POST`
- **Request Body:**
  ```json
  {
    "entity": "job",
    "id": "1234"
  }
  ```
- **Response:**
  ```json
  {
    "id": "1234",
    "data": { ... }
  }
  ```

### 2. Search for Matches

**Endpoint:** `/search-matches`

- **Method:** `POST`
- **Request Body:**
  ```json
  {
    "entity": "candidate",
    "id": "5678",
    "salary_match": true,
    "top_skill_match": true,
    "seniority_match": true,
    "from_index": 0,
    "size": 10
  }
  ```
- **Response:**
  ```json
  {
    "total_results": 5,
    "results": [ { ... }, { ... } ]
  }
  ```

## Running Tests

Run unit tests using:

```bash
pytest
```

## Deployment

To deploy with Docker:

```bash
docker-compose up -d
```

For a production setup, consider using a reverse proxy like Nginx and setting up Elasticsearch with proper security configurations.

## Loom Video Script

### Introduction

- Brief overview of the API functionality
- Technologies used (FastAPI, Elasticsearch, Docker)

### API Walkthrough

1. **Retrieve a document by ID** (Live demo in Postman/cURL)
2. **Search for matches** (Explaining filters & results)
3. **Code Structure** (Briefly explain key files: `main.py`, `services.py`, `tests/`)
4. **Running tests** (Show pytest execution)
5. **Docker Deployment** (Run API in a containerized environment)

### Conclusion

- Summary of features
- Potential improvements (Authentication, More filters)
- Call to action (Check GitHub repo, contribute, etc.)

