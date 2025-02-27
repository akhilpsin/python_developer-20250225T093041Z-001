import os
import sys
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import app, MAX_RESULT_SIZE

client = TestClient(app)

# Sample input Data
valid_entities = ["jobs", "candidates"]
invalid_entity = "invalid_entity"
valid_id = 7
invalid_id = 999999

# -----------------  Testing "get-entity"

def test_get_entity_valid():
    """Test fetching a valid jobs or candidates document."""
    for entity in valid_entities:
        response = client.post("/get-entity", json={"entity": entity, "id": valid_id})
        assert response.status_code == 200
        assert "id" in response.json()
        assert "data" in response.json()
    
def test_get_entity_invalid_id():
    """Test fetching a document with an invalid ID."""
    response = client.post("/get-entity", json={"entity": valid_entities[0], "id": invalid_id})
    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found"

def test_get_entity_invalid_entity():
    """Test fetching a document with an invalid entity."""
    response = client.post("/get-entity", json={"entity": invalid_entity, "id": valid_id})
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid entity type"

# -----------------  Testing "search-matches"

def test_search_matches_valid():
    """Test searching matches with valid entity and filters enabled."""
    for entity in valid_entities:
        response = client.post("/search-matches", json={
            "entity": entity,
            "id": valid_id,
            "filters": {
                "salary_match": True,
                "top_skill_match": True,
                "seniority_match": True,
                "minimum_should_match": 1
            },
            "from_index": 0,
            "size": 100
        })
        assert response.status_code == 200
        assert "total_results" in response.json()
        assert "results" in response.json()

def test_search_matches_invalid_entity():
    """Test searching with an invalid entity type."""
    response = client.post("/search-matches", json={
        "entity": invalid_entity,
        "id": valid_id,
        "filters": {
            "salary_match": True,
            "top_skill_match": True,
            "seniority_match": True,
            "minimum_should_match": 1
        },
        "from_index": 0,
        "size": 100
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid entity type"

def test_search_matches_invalid_id():
    """Test searching with a valid entity but invalid ID."""
    response = client.post("/search-matches", json={
        "entity": valid_entities[0],
        "id": invalid_id,
        "filters": {
            "salary_match": True,
            "top_skill_match": True,
            "seniority_match": True,
            "minimum_should_match": 1
        },
        "from_index": 0,
        "size": 100
    })
    assert response.status_code == 404
    assert response.json()["detail"] == "Target document not found"

def test_search_matches_max_size_limit():
    """Test searching when requesting more than MAX_RESULT_SIZE results."""
    response = client.post("/search-matches", json={
        "entity": valid_entities[0],
        "id": valid_id,
        "filters": {
            "salary_match": True,
            "top_skill_match": True,
            "seniority_match": True,
            "minimum_should_match": 1
        },
        "from_index": 0,
        "size": MAX_RESULT_SIZE + 100
    })
    assert response.status_code == 200
    assert response.json()["results"]
    assert len(response.json()["results"]) <= MAX_RESULT_SIZE

def test_search_matches_no_filters():
    """Test searching with all filters disabled to check if full data is fetched but Should still be within max limit"""
    response = client.post("/search-matches", json={
        "entity": valid_entities[0],
        "id": valid_id,
        "filters": {
            "salary_match": False,
            "top_skill_match": False,
            "seniority_match": False,
            "minimum_should_match": 0
        },
        "from_index": 0,
        "size": MAX_RESULT_SIZE + 100
    })
    assert response.status_code == 200
    assert response.json()["results"]
    assert len(response.json()["results"]) <= MAX_RESULT_SIZE

def test_search_matches_pagination():
    """Test pagination to check if results change when fetching next pages."""
    response_page_1 = client.post("/search-matches", json={
        "entity": valid_entities[0],
        "id": valid_id,
        "filters": {
            "salary_match": True,
            "top_skill_match": True,
            "seniority_match": True,
            "minimum_should_match": 1
        },
        "from_index": 0,
        "size": 10
    })

    response_page_2 = client.post("/search-matches", json={
        "entity": valid_entities[0],
        "id": valid_id,
        "filters": {
            "salary_match": True,
            "top_skill_match": True,
            "seniority_match": True,
            "minimum_should_match": 1
        },
        "from_index": 10,  # Next set of results
        "size": 10
    })

    assert response_page_1.status_code == 200
    assert response_page_2.status_code == 200
    assert response_page_1.json()["results"] != response_page_2.json()["results"]
