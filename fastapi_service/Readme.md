# **API Doccument**

## **Overview**
This FastAPI-based job recruitment API is designed to match job postings with potential candidates using Elasticsearch for efficient searching.

## **Features**
✅ Retrieve job or candidate details by ID
✅ Search for matching jobs or candidates with relevance scoring
✅ Supports filtering by salary, skills, and seniority
✅ Dockerized for easy deployment
✅ Includes unit tests for API validation

## **Installation**

### **Prerequisites**
- Docker & Docker Compose
- Python 3.8+
- Elasticsearch (Docker setup provided)

### **Running Locally**
1. Clone the repository:
   ```bash
   git clone "https://github.com/akhilpsin/python_developer-20250225T093041Z-001.git"
   cd python_developer-20250225T093041Z-001
   ```
2. Start all services using Docker Compose:
   ```bash
   docker-compose up --build
   ```
3. Access the API at:
   - **Base URL:** `http://localhost:8000`  
   - **Interactive FastAPI Docs API Docs:** `http://127.0.0.1:8000/docs`
   - **Alternative Swagger UI (ReDoc):** `http://127.0.0.1:8000/redoc`

---

## **API Endpoints**

### **1. Retrieve Document by ID**
Fetch details of a specific job or candidate using their ID.

- **Endpoint:** `/get-entity`
- **Method:** `POST`
- **Request Body:**
  ```json
  {
    "entity": "jobs",
    "id": "12"
  }
  ```
  **Request Fields:**
  - `entity` _(string)_: `"jobs"` or `"candidates"`
  - `id` _(string/int)_: The unique identifier of the job or candidate

- **Response:**
  ```json
  {
    "id": "12",
    "data": { ... }
  }
  ```
  
🔹 **Sample cURL Request:**
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/get-entity' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "entity": "jobs",
  "id": 1
}'
```

---

### **2. Search for Matches**
Find matching job postings or candidates based on filters like salary, skills, and seniority level.

- **Endpoint:** `/search-matches`
- **Method:** `POST`
- **Request Body:**
  ```json
  {
    "entity": "jobs",
    "id": 4,
    "filters": {
      "salary_match": true,
      "top_skill_match": true,
      "seniority_match": true,
      "minimum_should_match": 2
    },
    "from_index": 0,
    "size": 100
  }
  ```
  
  **Request Fields:**
  - `entity` _(string)_: `"jobs"` or `"candidates"`
  - `id` _(string/int)_: The unique ID of the job or candidate to match against
  - `filters` _(object)_: Criteria for matching
    - `salary_match` _(boolean)_: Whether salary should match
    - `top_skill_match` _(boolean)_: Whether top skills should match
    - `seniority_match` _(boolean)_: Whether seniority level should match
    - `minimum_should_match` _(int)_: Minimum number of filter conditions that should match
  - `from_index` _(int)_: Pagination start index
  - `size` _(int)_: Number of results to return

- **Response:**
  ```json
  {
    "total_results": 5,
    "results": [ { ... }, { ... } ]
  }
  ```
  
🔹 **Sample cURL Request:**
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/search-matches' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "entity": "jobs",
  "id": 4,
  "filters": {
    "salary_match": true,
    "top_skill_match": true,
    "seniority_match": true,
    "minimum_should_match": 2
  },
  "from_index": 0,
  "size": 100
}'
```

---

## **Running Tests**
To run unit tests, use:
```bash
pytest
```

---

## **Deployment**
To deploy the API using Docker:
```bash
docker-compose up -d
```
👉 **Note:** The entire project directory must be run for the API to function correctly.