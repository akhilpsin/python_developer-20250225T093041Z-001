from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from elasticsearch import Elasticsearch

app = FastAPI()
MAX_RESULT_SIZE = 200  # Limit on the number of results per request

# Elasticsearch client
def get_es():
    #return Elasticsearch("http://localhost:9200") #for local run
    return Elasticsearch("http://elasticsearch:9200") #for docker

# Request Models
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

# Validate entity type
def validate_entity(entity: str):
    if entity not in ["jobs", "candidates"]:
        raise HTTPException(status_code=400, detail="Invalid entity type")

# Build Elasticsearch query based on filters
def build_query(entity: str, target: dict, filters: SearchFilters):
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
            else {"terms": {"seniorities": [target["seniority"]]}}
        )

    # If no filters then fetch all results
    if not search_filters:
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

# Retrieve a specific job or candidate document from Elasticsearch
@app.post("/get-entity")
def get_entity(request: EntityRequest, es: Elasticsearch = Depends(get_es)):
    validate_entity(request.entity)
    try:
        doc = es.get(index=request.entity, id=request.id)
        return {"id": doc["_id"], "data": doc["_source"]}
    except Exception:
        raise HTTPException(status_code=404, detail="Document not found")

# Search for matching jobs or candidates based on filters
@app.post("/search-matches")
def search_matches(request: SearchRequest, es: Elasticsearch = Depends(get_es)):
    validate_entity(request.entity)
    index = "candidates" if request.entity == "jobs" else "jobs"

    try:
        target_doc = es.get(index=request.entity, id=request.id)
        target = target_doc["_source"]
    except Exception:
        raise HTTPException(status_code=404, detail="Target document not found")

    query = build_query(request.entity, target, request.filters)
    query["from"] = request.from_index
    query["size"] = min(request.size, MAX_RESULT_SIZE)  # Applying size limit

    response = es.search(index=index, body=query)

    return {
        "total_results": response["hits"]["total"]["value"],
        "results": [{"id": hit["_id"], "relevance_score": hit["_score"]} for hit in response["hits"]["hits"]]
    }
