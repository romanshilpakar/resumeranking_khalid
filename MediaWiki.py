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


# import requests

# def get_summary(search_query):
#     endpoint = f"https://en.wikipedia.org/api/rest_v1/page/summary/{search_query}"
#     response = requests.get(endpoint)
#     data = response.json()
#     summary = data.get("extract", "")
#     return summary

# def get_summaries_for_queries(search_queries):
#     summaries = []
#     for search_query in search_queries:
#         summary = get_summary(search_query)
#         if summary:
#             summaries.append(summary)
#     return summaries


# import requests

# # Replace these with your own credentials
# api_username = "roman"
# api_password = "Iamroman2056$"

# def get_summary(search_query):
#     endpoint = f"https://en.wikipedia.org/api/rest_v1/page/summary/{search_query}"
#     response = requests.get(endpoint, auth=(api_username, api_password))
#     data = response.json()
#     summary = data.get("extract", "")
#     return summary

# def get_summaries_for_queries(search_queries):
#     summaries = []
#     for search_query in search_queries:
#         summary = get_summary(search_query)
#         if summary:
#             summaries.append(summary)
#     return summaries

# from gensim.summarization import summarize

# def get_gensim_summary(text):
#     # You may need to experiment with the ratio parameter to get the desired summary length
#     summary = summarize(text, ratio=0.2)
#     return summary

# def get_summaries_for_queries(search_queries):
#     summaries = []
#     for search_query in search_queries:
#         # Assuming that search_query is a document or text for which you want a summary
#         summary = get_gensim_summary(search_query)
#         if summary:
#             summaries.append(summary)
#     return summaries

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

def get_sumy_summary(text):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, 3)  # 3 is the number of sentences in the summary
    return " ".join(str(sentence) for sentence in summary)

def get_summaries_for_queries(search_queries):
    summaries = []
    for search_query in search_queries:
        # Assuming that search_query is a document or text for which you want a summary
        summary = get_sumy_summary(search_query)
        if summary:
            summaries.append(summary)
    return summaries



