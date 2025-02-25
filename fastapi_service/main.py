from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from elasticsearch import Elasticsearch

app = FastAPI()
es = Elasticsearch("http://elasticsearch:9200")

class SearchFilters(BaseModel):
    salary_match: bool = False
    top_skill_match: bool = False
    seniority_match: bool = False

@app.post("/{entity}/{id}")
def get_entity(entity: str, id: int):
    if entity not in ["jobs", "candidates"]:
        raise HTTPException(status_code=400, detail="Invalid entity type")
    
    doc = es.get(index=entity, id=id, ignore=[404])
    if not doc or "found" not in doc or not doc["found"]:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {"id": doc["_id"], "data": doc["_source"]}

@app.post("/search/{entity}/{id}")
def search_matches(entity: str, id: int, filters: SearchFilters):
    if entity not in ["jobs", "candidates"]:
        raise HTTPException(status_code=400, detail="Invalid entity type")
    
    index = "candidates" if entity == "jobs" else "jobs"
    target_doc = es.get(index=entity, id=id, ignore=[404])
    if not target_doc or "found" not in target_doc or not target_doc["found"]:
        raise HTTPException(status_code=404, detail="Target document not found")
    
    target = target_doc["_source"]
    search_filters = []
    
    if filters.salary_match:
        salary_key = "salary_expectation" if entity == "jobs" else "max_salary"
        salary_value = {"lte": target["max_salary"]} if entity == "jobs" else {"gte": target["salary_expectation"]}

        salary_filter = {"range": {salary_key: salary_value}}

        search_filters.append(salary_filter)
    
    if filters.top_skill_match:
        min_skills = min(len(target["top_skills"]), 2)
        skills_filter = {"terms_set": {"top_skills": {"terms": target["top_skills"], "minimum_should_match_script": {"source": f"Math.max(doc['top_skills'].size(), {min_skills})"}}}}
        search_filters.append(skills_filter)
    
    if filters.seniority_match:
        seniority_value = target.get("seniority", None)
        if seniority_value:
            seniority_filter = {"terms": {"seniorities" if entity == "jobs" else "seniority": seniority_value}}
            search_filters.append(seniority_filter)
    
    query = {"query": {"bool": {"should": search_filters}}} if search_filters else {"query": {"match_all": {}}}
    
    response = es.search(index=index, body=query)
    results = [{"id": hit["_id"], "relevance_score": hit["_score"], "data": hit["_source"]} for hit in response["hits"]["hits"]]
    
    return results