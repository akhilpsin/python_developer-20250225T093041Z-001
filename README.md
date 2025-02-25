# Intro

For your next step in the application process at Instaffo we'd like you to do the task given below to be able to further assess your skills and knowledge. 

**Submission Guidelines:**

✅ **Code Submission**: Please upload your solution to a **publicly accessible Git repository** and share the link with the person managing your application (e.g., via the chat on instaffo.com).

✅ **Video Explanation (Optional but Preferred)**: If possible, please record a **short video** explaining your overall solution (e.g., using [Loom](https://www.loom.com/screen-recorder)), and share the link with us.

Code quality (including project structure), dependencies and environment management, documentation (docstrings, comments, README file, etc.) are of utmost importance!

We wish you good luck (and also a lot of fun) with the task! 🍀

# Matching talents and jobs

Instaffo is a recruiting platform that makes money by bringing together hiring companies and talents. Companies offer job opportunities and need the right talents to fill their open job positions, talents on the other hand are looking for new job opportunities.

One core component of the Instaffo platform is the search functionality, which e.g. enables talents to only see relevant job opportunities.

# Task

You are provided with data and a docker-compose.yml file which initializes and populates __2 ES indices - for candidates and jobs__. 

🎯 Your goal is to create a way for the outside world to communicate with the ES indices.

📌 Implement 2 core functionalities:

1. Implement a functionality that, given an ID for either a job or a candidate, retrieves the corresponding document from the ES index.
2. Implement a functionality that, given a job ID or candidate ID, retrieves the corresponding candidates or jobs that match the user’s specified filters. The return value should contain the following fields - id of the matching documents as `id` and the relevance scores as `relevance_score`.
    - The filters, available to the user should be at least 2 of the following: `salary_match`, `top_skill_match` and `seniority_match`.
        - The `salary_match` filter should return jobs that have `gte` `max_salary` than the candidate's `salary_expectation` and should return candidates that have `lte` `salary_expectation` than a job's `max_salary`
        - The `top_skill_match` filter should return jobs/candidates that share at least min(<n_query_top_skills>, 2) of the top skills with the target document (job or candidate). Here, n_query_top_skills is the total number of top skills for the entity whose relevant matches we want to find. For example, if we are looking for relevant jobs for a given candidate, n_query_top_skills refers to the number of top skills that candidate has.
        - The `seniority_match` filter should return jobs/candidates where there is a match in the `seniorities` of a job and the `seniority` of a candidate.
    - The filters should be usable together, concatenated by the `OR` logical operator (`"should"` query in Elasticsearch).

    💡 The `_es_example.py` file provides examples on query building for all the required filters.  

Finally, update the existing docker-compose.yml file to include your new service, ensuring it can be accessed via HTTP requests. Additionally, provide a report on test coverage as part of your submission.
In your implementation you should abide to the principles of writing clean code and to the RestAPI design principles.

🪲 What we will assess:

- ❗ clean code
- ❗ well-defined api
- ❗ overall project structure
- 👶 some API tests **need** to be present but do **not** need to be detailed, devote only minimum effort, enough to showcase your understanding on how unit tests should be written.

## Good luck! 🚀