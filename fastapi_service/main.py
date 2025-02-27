import os
import logging
from pydantic import BaseModel
from elasticsearch import Elasticsearch
from fastapi import FastAPI, HTTPException, Depends

# Logging configuration
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/api.log", level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s")

logger = logging.getLogger(__name__)

app = FastAPI()
MAX_RESULT_SIZE = 200  # Limit on the number of results per request

# Elasticsearch client
def get_es():
    logger.info("Connecting to Elasticsearch")
    return Elasticsearch("http://elasticsearch:9200")  # for Docker

# Request models
class SearchFilters(BaseModel):
    salary_match: bool = True
    top_skill_match: bool = True
    seniority_match: bool = True
    minimum_should_match: int = 1

class SearchRequest(BaseModel):
    entity: str
    id: int
    filters: SearchFilters
    from_index: int = 0
    size: int = 100

class EntityRequest(BaseModel):
    entity: str
    id: int

# Validating entity type
def validate_entity(entity: str):
    if entity not in ["jobs", "candidates"]:
        logger.warning(f"Invalid entity type requested: {entity}")
        raise HTTPException(status_code=400, detail="Invalid entity type")

# Building elasticsearch with filters
def build_query(entity: str, target: dict, filters: SearchFilters):
    logger.info(f"Building query for entity: {entity}, ID: {target.get('id', 'unknown')}")
    search_filters = []

    if filters.salary_match:
        search_filters.append(
            {"range": {"salary_expectation": {"lte": target["max_salary"]}}} if entity == "jobs"
            else {"range": {"max_salary": {"gte": target["salary_expectation"]}}}
        )

    if filters.top_skill_match and target.get("top_skills"):
        search_filters.append({
            "terms_set": {
                "top_skills": {
                    "terms": target["top_skills"],
                    "minimum_should_match_script": {
                        "source": "Math.min(params.num_terms, 2)",
                        "params": {"num_terms": len(target["top_skills"])}
                    }
                }
            }
        })

    if filters.seniority_match and "seniorities" in target:
        search_filters.append(
            {"terms": {"seniority": target["seniorities"]}} if entity == "jobs"
            else {"terms": {"seniorities": [target["seniority"]]}},
        )

    if not search_filters:
        logger.info("No filters applied, fetching all results")
        return {"query": {"match_all": {}}, "sort": [{"_score": "desc"}]}

    return {
        "query": {
            "bool": {
                "should": search_filters,
                "minimum_should_match": filters.minimum_should_match
            }
        },
        "sort": [{"_score": "desc"}]
    }

# Retrieveing specific job or candidate document from Elasticsearch
@app.post("/get-entity")
def get_entity(request: EntityRequest, es: Elasticsearch = Depends(get_es)):
    validate_entity(request.entity)
    logger.info(f"Fetching document: Entity={request.entity}, ID={request.id}")
    
    try:
        doc = es.get(index=request.entity, id=request.id)
        logger.info(f"Document found: {request.id}")
        return {"id": doc["_id"], "data": doc["_source"]}
    except Exception as e:
        logger.error(f"Document not found: Entity={request.entity}, ID={request.id}. Error: {str(e)}")
        raise HTTPException(status_code=404, detail="Document not found")

# Search for matching jobs or candidates based on filters
@app.post("/search-matches")
def search_matches(request: SearchRequest, es: Elasticsearch = Depends(get_es)):
    validate_entity(request.entity)
    index = "candidates" if request.entity == "jobs" else "jobs"
    
    logger.info(f"Searching matches for: Entity={request.entity}, ID={request.id}")

    try:
        target_doc = es.get(index=request.entity, id=request.id)
        target = target_doc["_source"]
    except Exception as e:
        logger.error(f"Target document not found: Entity={request.entity}, ID={request.id}. Error: {str(e)}")
        raise HTTPException(status_code=404, detail="Target document not found")

    query = build_query(request.entity, target, request.filters)
    query["from"] = request.from_index
    query["size"] = min(request.size, MAX_RESULT_SIZE)

    response = es.search(index=index, body=query)
    logger.info(f"Search completed: Entity={request.entity}, ID={request.id}, Total Results={response['hits']['total']['value']}")

    return {
        "total_results": response["hits"]["total"]["value"],
        "results": [{"id": hit["_id"], "relevance_score": hit["_score"]} for hit in response["hits"]["hits"]]
    }
