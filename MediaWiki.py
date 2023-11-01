# import requests

# def get_search_results(search_query):
#     endpoint = f"https://en.wikipedia.org/w/api.php?action=query&list=search&format=json&utf8=1&redirects=1&srprop=size&origin=*&srsearch={search_query}"
#     response = requests.get(endpoint)
#     data = response.json()
#     results = data.get("query", {}).get("search", [])
#     if len(results) > 0:
#         titles = "|".join(result.get("title", "") for result in results)
#         if titles:
#             return get_summary(titles)
#     return None

# def get_summary(titles):
#     endpoint = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts&format=json&exsentences=5&explaintext=&origin=*&titles={titles}"
#     response = requests.get(endpoint)
#     data = response.json()
#     results = data.get("query", {}).get("pages", {})
#     summaries = [result.get("extract", "") for result in results.values()]
#     return summaries

# def get_summaries_for_queries(search_queries):
#     summaries = []
#     for search_query in search_queries:
#         results = get_search_results(search_query)
#         if results:
#             summaries.append(results[0])  # Get the first summary for each query
#     return summaries


import requests

def get_summary(search_query):
    endpoint = f"https://en.wikipedia.org/api/rest_v1/page/summary/{search_query}"
    response = requests.get(endpoint)
    data = response.json()
    summary = data.get("extract", "")
    return summary

def get_summaries_for_queries(search_queries):
    summaries = []
    for search_query in search_queries:
        summary = get_summary(search_query)
        if summary:
            summaries.append(summary)
    return summaries
