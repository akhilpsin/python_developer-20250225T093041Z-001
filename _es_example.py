from es_lib import ElasticsearchClient

client = ElasticsearchClient("candidates")

print(client.get_entity(id=10))
print("\n\n\n")
# Retrieve documents whose top skills exactly match the list of terms
print(
    client.search(
        query={
            "query": {
                "bool": {
                    "must": [
                        {
                            "terms_set": {
                                "top_skills": {
                                    "terms": ["python", "javascript", "java"],
                                    "minimum_should_match_script": {
                                        "source": "Math.max(doc['top_skills'].size(), params.num_terms)"
                                    },
                                }
                            }
                        },
                        {"terms": {"other_skills": ["git"]}},
                    ]
                }
            }
        }
    )
)
print("\n\n\n")
print(
    client.search_with_bool_queries(
        should_queries=[
            {"terms": {"seniorities": ["junior"]}},
            {"terms": {"other_skills": ["ui/ux"]}},
        ],
        must_queries=[{"range": {"salary_expectation": {"lte": 40000}}}],
    )
)
